# DrResult

More radical approach to Rust's `std::result` in Python.

## Motivation

I do not want exceptions in my code.
Rust has this figured out quite neatly
by essentially revolving around two pathways for errors:
A possible error condition is either one that has no prospect of being handled
-- then the program should terminate -- or it is one that could be handled --
then it has to be handled or explicitly ignored.

This concept is replicated here by using `AssertionError` to emulate Rust's `panic!`,
mapping all unhandled exceptions to `AssertionError`
and providing a Rust-like `result` type to signal error conditions that do not need to terminate
the program.

## Documentation

### Basic Usage

```python
from drresult import Ok, Err, returns_result

@returns_result()
def read_file():
    with open('/this/path/is/invalid') as f:
        return Ok(f.read())

result = func()
```
This will raise an `AssertionError` due to an unhandled exception.

But if you specify the exceptions you expect, you can handle the error:
```python
@returns_result(FileNotFoundError)
def read_file():
    with open('/this/path/is/invalid') as f:
        return Ok(f.read())

result = func()
if result.is_ok():
    print(f'File content: {result.unwrap()}')
else:
    print(f'Error: {result.unwrap_err()}')
```

Or -- if you are feeling fancy -- you can do pattern matching:
```python
@returns_result(FileNotFoundError)
def read_file():
    with open('/this/path/is/invalid') as f:
        return f.read()

result = read_file()
match result:
    case Ok(v):
        print(f'File content: {v}')
    case Err(e):
        print(f'Error: {e}')
```

And even fancier:
```python
data = [
    { 'foo': 'value-1' },
    { 'bar': 'value-2' }
]

@returns_result(IndexError, KeyError)
def retrieve_record_entry_backend(index, key):
    return Ok(data[index][key])

def retrieve_record_entry(index, key):
    match retrieve_record_entry_backend(index, key):
        case Ok(v):
            print(f'Retrieved: {v}')
        case Err(IndexError()):
            print(f'No such record: {index}')
        case Err(KeyError()):
            print(f'No entry `{key}` in record {index}')

retrieve_record_entry(2, 'foo')    # No such record: 2
retrieve_record_entry(1, 'foo')    # No entry `foo` in record 1
retrieve_record_entry(1, 'bar')    # Retrieved: value-2
```

### Typing

```python
from typing import NoReturn
from drresult import Result, Ok, Err, returns_result

data = [{'foo': 'value-1'}, {'bar': 'value-2'}]


@returns_result(IndexError, KeyError)
def retrieve_record_entry_backend(index: int, key: str) -> Result[str, int]:
    if key == 'baz':
        return Err(1)
    return Ok(data[index][key])


def retrieve_record_entry(index: int, key: str) -> str:
    match retrieve_record_entry_backend(index, key):
        case Ok(v):
            return f'Retrieved: {v}'
        case Err(IndexError()):
            return f'No such record: {index}'
        case Err(KeyError()):
            return f'No entry `{key}` in record {index}'
        case Err(e):
            return f'Error: {e}'
        case _:
            assert False


print(retrieve_record_entry(2, 'foo'))
print(retrieve_record_entry(1, 'foo'))
print(retrieve_record_entry(1, 'bar'))
print(retrieve_record_entry(1, 'baz'))
```
As you can see from this example, the `@returns_result` decorator extends the return type of the function from `Result[T, E]` to `Result[T, E | Exception]`.

## Similar Projects

For a less extreme approach on Rust's result type, see:

* [https://github.com/rustedpy/result](https://github.com/rustedpy/result)
* [https://github.com/felixhammerl/resultify](https://github.com/felixhammerl/resultify)
