"""Offline integration contracts with fake helper outputs; no MySQL or API calls."""
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from week9.orchestrator import orchestrate, plan, ORDER


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'IDX_WEEK9_SESSION_DIR': self.temp.name})
        self.env.start()
        self.calls = []

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def fake(self, name, request):
        self.calls.append((name, request))
        if name == ORDER[0]:
            return {'properties': [{'listingId': '123', 'address': 'Example', 'price': 800000}]}
        if name == ORDER[3]:
            return 'DOM means Days on Market [S1].\n\nSources:\n[S1] Primer.pdf - page 6'
        return {'reference': request['listing_id'], 'city': request['filters'].get('city')}

    def run_query(self, query, session='one', **kwargs):
        return orchestrate(query, session, runner=self.fake, **kwargs)

    def test_all_routes(self):
        cases = [('Find homes in Irvine', ORDER[0]), ('Market trends in Irvine', ORDER[1]),
                 ('Recommend similar homes to listing 123', ORDER[2]), ('What is DOM?', ORDER[3]),
                 ('Draft an email', 'emailDraftAgent')]
        for query, expected in cases:
            self.assertIn(expected, plan(query))

    def test_definition_not_market(self):
        self.assertEqual(plan('What is Days on Market?'), [ORDER[3]])

    def test_mixed_parallel_execution(self):
        barrier = threading.Barrier(2)
        def runner(name, request):
            barrier.wait(timeout=3)
            return self.fake(name, request)
        result = orchestrate('Find homes in Pasadena and tell me whether prices are rising', 'one', runner=runner)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['agents'], list(ORDER[:2]))

    def test_missing_city_does_not_query(self):
        result = self.run_query('Find homes under $900k')
        self.assertEqual(result['status'], 'clarification')
        self.assertEqual(self.calls, [])

    def test_missing_reference(self):
        self.assertEqual(self.run_query('Recommend similar homes')['status'], 'clarification')

    def test_followup_and_recommendation(self):
        self.run_query('Find condos in Irvine under $900k')
        self.run_query('Under $850k')
        self.assertEqual(self.calls[-1][1]['filters']['maxPrice'], 850000)
        self.assertEqual(self.calls[-1][1]['filters']['city'], 'Irvine')
        self.run_query('Recommend similar homes')
        self.assertEqual(self.calls[-1][1]['listing_id'], '123')

    def test_session_isolation_and_reset(self):
        self.run_query('Find homes in Irvine')
        self.assertEqual(self.run_query('Recommend similar homes', session='other')['status'], 'clarification')
        self.run_query('Start over')
        self.assertEqual(self.run_query('Recommend similar homes')['status'], 'clarification')

    def test_citations_preserved(self):
        result = self.run_query('What is DOM?')
        self.assertIn('[S1] Primer.pdf - page 6', result['response'])

    def test_partial_failure_sanitizes_error(self):
        def runner(name, request):
            if name == ORDER[1]:
                raise RuntimeError('password=secret')
            return self.fake(name, request)
        result = orchestrate('Find homes in Irvine and show market trends', 'one', runner=runner)
        self.assertEqual(result['status'], 'partial')
        self.assertIn('Example', result['response'])
        self.assertNotIn('password', str(result))

    def test_email_uses_fresh_evidence(self):
        result = self.run_query('Find homes in Irvine and draft an email')
        self.assertEqual(result['status'], 'ok')
        self.assertIn('Subject:', result['response'])
        self.assertIn('800000', result['response'])

    def test_email_uses_saved_evidence(self):
        self.run_query('What is DOM?')
        self.assertIn('[S1] Primer.pdf - page 6', self.run_query('Draft an email')['response'])

    def test_no_email_when_no_evidence(self):
        self.assertEqual(self.run_query('Draft an email')['status'], 'clarification')

    def test_failed_fresh_email_does_not_use_old_evidence(self):
        self.run_query('Find homes in Irvine')
        def failure(name, request):
            raise RuntimeError('failed')
        result = orchestrate('Draft a market summary email in Pasadena', 'one', runner=failure)
        self.assertNotIn('Subject:', result['response'])
        self.assertNotIn('Example', result['response'])

    def test_explicit_hints(self):
        result = self.run_query('Pasadena overview', city='Pasadena', agents=[ORDER[1]])
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(self.calls[-1][1]['filters']['city'], 'Pasadena')

    def test_validation(self):
        for options in [{'months': 0}, {'as_of': 'bad-date'}, {'agents': ['unknown']}]:
            with self.assertRaises(ValueError):
                self.run_query('Find homes in Irvine', **options)
        with self.assertRaises(ValueError):
            self.run_query('')


if __name__ == '__main__':
    unittest.main()
