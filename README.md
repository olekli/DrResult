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

#### `@noexcept`

If your function knows no errors, you mark it as `@noexcept()`:

```python
from drresult import noexcept

@noexcept()
def sum(a: list) -> int:
    result = 0
    for item in a:
        result += item
    return result

result = func([1, 2, 3])
```

This will do what you expect it does.
But if you screw up...
```python
@noexcept()
def sum(a: list) -> int:
    result = 0
    for item in a:
        result += item
    print(a[7])   # IndexError
    return result

result = func([1, 2, 3])    # AssertionError
```
... then it will raise an `AssertionError` preserving the stack trace and the message of the original exception.

This way all unexpected exceptions are normalised to `AssertionError`.

#### `@returns_result()`

Marking a function as `@returns_result` will wrap its return value in an `Ok` result
and exceptions thrown in an `Err` result. But only those exceptions that you specify:

```python
@returns_result(FileNotFoundError)
def read_file() -> str:
    with open('/some/path/that/might/be/invalid') as f:
        return f.read()

result = func()
if result.is_ok():
    print(f'File content: {result.unwrap()}')
else:
    print(f'Error: {result.unwrap_err()}')
```

This will do as you expect.


If fail to specify an exception that is raised...

```python
from drresult import returns_result

@returns_result(IndexError, KeyError)
def read_file() -> str:
    with open('/this/path/is/invalid') as f:
        return f.read()

result = func()    # AssertionError
```
.. it will be re-raised as `AssertionError`.

Or -- if you are feeling fancy -- you can do pattern matching:
```python
@returns_result(FileNotFoundError)
def read_file() -> str:
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
data = [{ 'foo': 'value-1' }, { 'bar': 'value-2' }]

@returns_result(IndexError, KeyError, RuntimeError)
def retrieve_record_entry_backend(index: int, key: str) -> str:
    if key == 'baz':
        raise RuntimeError('Cannot process baz!')
    return data[index][key]

def retrieve_record_entry(index: int, key: str):
    match retrieve_record_entry_backend(index: int, key: str):
        case Ok(v):
            print(f'Retrieved: {v}')
        case Err(IndexError()):
            print(f'No such record: {index}')
        case Err(KeyError()):
            print(f'No entry `{key}` in record {index}')
        case Err(RuntimeError() as e):
            print(f'Error: {e}')

retrieve_record_entry(2, 'foo')    # No such record: 2
retrieve_record_entry(1, 'foo')    # No entry `foo` in record 1
retrieve_record_entry(1, 'bar')    # Retrieved: value-2
retrieve_record_entry(1, 'baz')    # Error: Cannot process baz!
```

#### Implicit conversion to bool

If you are feeling more lazy than fancy, you can do this:
```python
result = Ok('foo')
assert result

result = Err('bar')
assert not result
```

## Similar Projects

For a less extreme approach on Rust's result type, see:

* [https://github.com/rustedpy/result](https://github.com/rustedpy/result)
* [https://github.com/felixhammerl/resultify](https://github.com/felixhammerl/resultify)
