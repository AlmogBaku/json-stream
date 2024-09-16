import unittest
from typing import Generator

from json_streamer import JsonParser, ParseState, loads


def stream_json(value: str, chunk_size: int = 4) -> Generator[str, None, None]:
    for i in range(0, len(value), chunk_size):
        yield value[i:i + chunk_size]


class TestStreamJson(unittest.TestCase):

    TEST_CASES = (
        {
            'input': '{"field1": "value1", "field2": 42}',
            'parse_fn': lambda s: loads(s),
            'expected_states': [
                (ParseState.PARTIAL, {'field1': ''}),
                (ParseState.PARTIAL, {'field1': 'valu'}),
                (ParseState.PARTIAL, {'field1': 'value1', 'field2': 4}),
                (ParseState.COMPLETE, {'field1': 'value1', 'field2': 42})
            ],
        },
        {
            'input': '{"field1": "value1", "field2": "multi-line\n\nvalue"}',
            'parse_fn': lambda s: loads(s),
            'expected_states': [
                (ParseState.PARTIAL, {'field1': ''}),
                (ParseState.PARTIAL, {'field1': 'valu'}),
                (ParseState.PARTIAL, {'field1': 'value1', 'field2': ''}),
                (ParseState.PARTIAL, {'field1': 'value1', 'field2': 'mult'}),
                (ParseState.PARTIAL, {'field1': 'value1', 'field2': 'multi-li'}),
            ],
        },
        {
            'input': '{"field1": "value1", "field2": "multi-line\n\nvalue"}',
            'parse_fn': lambda s: loads(s, parser=JsonParser(strict=False)),
            'expected_states': [
                (ParseState.PARTIAL, {'field1': ''}),
                (ParseState.PARTIAL, {'field1': 'valu'}),
                (ParseState.PARTIAL, {'field1': 'value1', 'field2': ''}),
                (ParseState.PARTIAL, {'field1': 'value1', 'field2': 'mult'}),
                (ParseState.PARTIAL, {'field1': 'value1', 'field2': 'multi-li'}),
                (ParseState.PARTIAL, {'field1': 'value1', 'field2': 'multi-line\n\n'}),
                (ParseState.PARTIAL, {'field1': 'value1', 'field2': 'multi-line\n\nvalu'}),
                (ParseState.COMPLETE, {'field1': 'value1', 'field2': 'multi-line\n\nvalue'})
            ],
        },
    )

    def test_stream_json(self):
        for test_case in self.TEST_CASES:
            with self.subTest(test_case=test_case):
                mystream = stream_json(test_case['input'])
                ret = test_case['parse_fn'](mystream)
                self.assertListEqual(list(ret), test_case['expected_states'])


if __name__ == '__main__':
    unittest.main()
