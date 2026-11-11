import unittest

from agent import evidence_observation, related_incidents, run_agent
from status_tools import StatusTools
from test_lab import FakeProvider, final, tool_call


class EvidenceTests(unittest.TestCase):
    def test_counts_do_not_replace_original_result(self):
        original = {'incidents': [{'id': 'sample'}], 'matching_incidents_in_last_50': 12}
        observation = evidence_observation('get_status', {}, original)
        self.assertEqual(observation['_agent_evidence']['displayed_incidents'], 1)
        self.assertEqual(observation['_agent_evidence']['matching_incidents'], 12)
        self.assertNotIn('_agent_evidence', original)

    def test_only_supported_incident_links_are_followed(self):
        result = {'ok': True, 'updates': [{'body': 'See https://www.githubstatus.com/incidents/example123 and https://untrusted.example/incidents/other'}]}
        self.assertEqual(related_incidents(result), {('github', 'example123')})

    def test_unread_reference_prevents_premature_completion(self):
        class LinkedTools(StatusTools):
            def execute(self, name, args):
                return {'ok': True, 'url': 'https://www.githubstatus.com/incidents/first',
                        'updates': [{'body': 'See https://www.githubstatus.com/incidents/second'}]}

        provider = FakeProvider([
            tool_call('first-call', 'get_incident_details', '{"provider":"github","incident_id":"first"}'),
            final('Chưa có nguyên nhân. https://www.githubstatus.com/incidents/first'),
        ])
        result = run_agent('Tìm nguyên nhân sự cố', provider, LinkedTools(), max_steps=2)
        self.assertEqual(result['status'], 'max_steps')
        self.assertTrue(any(event['event'] == 'validation_unread_reference' for event in result['trace']))


if __name__ == '__main__':
    unittest.main()
