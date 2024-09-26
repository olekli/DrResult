# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from typing import Type

from drresult import gather_result, Ok, Err, returns_result, Result

import pytest
import os
import json


def test_no_result_is_ok_none():
    with gather_result() as result:
        pass
    result = result.get()
    assert result.unwrap() == None


def test_no_error_receives_ok():
    with gather_result() as result:
        result.set(Ok('foo'))
    result = result.get()
    assert result.unwrap() == 'foo'


def test_expected_error_receives_err():
    with gather_result() as result:
        result.set(Ok('foo'))
        raise RuntimeError('bar')
    result = result.get()
    err = result.unwrap_err()
    assert isinstance(err, RuntimeError)
    assert str(err) == 'bar'


def test_unexpected_error_raises_assertion():
    with pytest.raises(AssertionError):
        with gather_result(expects=[IndexError, KeyError]) as result:
            result.set(Ok('foo'))
            raise RuntimeError('bar')


def test_assertion_is_unhandled():
    with pytest.raises(AssertionError):
        with gather_result() as result:
            assert False
            result.set(Ok('foo'))


def test_example(tmp_path):
    @returns_result()
    def parse_json_file(filename: str) -> Result[dict]:
        with gather_result() as result:
            with open(filename) as f:
                result.set(Ok(json.loads(f.read())))
        result = result.get()
        match result:
            case Ok(data):
                return Ok(data)
            case Err(FileNotFoundError()):
                return Ok({})
            case _:
                return result

    non_existing_path = os.path.join(tmp_path, 'non-existing.json')
    result = parse_json_file(non_existing_path)
    assert result == Ok({})

    existing_path = os.path.join(tmp_path, 'existing.json')
    with open(existing_path, 'w') as f:
        f.write(json.dumps({'foo': 'bar', 'baz': 123}))
    result = parse_json_file(existing_path)
    assert result == Ok({'foo': 'bar', 'baz': 123})

    existing_but_broken_path = os.path.join(tmp_path, 'existing-but-broken.json')
    with open(existing_but_broken_path, 'w') as f:
        f.write('Whoops, this is not a JSON')
    result = parse_json_file(existing_but_broken_path)
    assert not result
    assert isinstance(result.unwrap_err(), json.JSONDecodeError)
