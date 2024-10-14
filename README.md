# DrResult

More radical approach to Rust's `std::result` in Python.

## Motivation

I do not want exceptions in my code.
Rust has this figured out quite neatly
by essentially revolving around two pathways for errors:
A possible error condition is either one that has no prospect of being handled
-- then the program should terminate -- or it is one that could be handled --
then it has to be handled or explicitly ignored.

This concept is replicated here by using mapping all unhandled exceptions to `Panic`
and providing a Rust-like `result` type to signal error conditions that do not need to terminate
the program.

## Documentation

### Concept

At each point in your code, there are exceptions that are considered to be expected
and there are exceptions that are considered unexpected.

In general, an unexpected exception will be mapped to `Panic`.
No part of DrResult will attempt to handle a `Panic` exception.
And you should leave all exception handling to DrResult,
i.e. have no `try/except` blocks in your code.
In any case, you should never catch `Panic`.
An unexpected exception will therefore result in program termination with stack unwinding.

You will need to specify which exceptions are to be expected.
There are two modes of operation here:
You can explicitly name the exceptions to be expected in a function.
Or you can skip that and basically expect all exceptions.

_Basically_ means: By default only `Exception` is expected, not `BaseException`.
And even of type `Exception` that are some considered to be never expected:
```python
AssertionError, AttributeError, ImportError, MemoryError, NameError, SyntaxError, SystemError, TypeError
```
If you do not explicitly expect these, they will be implicitly unexpected.
(Obviously, the exact list may be up for debate.)

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

result = func([1, 2, 3])    # Panic!
```
... then it will raise `Panic` preserving the stack trace and the original exception.

This way all unexpected exceptions are normalised to `Panic`.

Please note that a `@noexecpt` function does not return a result but just the return type itself.

#### `@returns_result()` and `expects`

Marking a function as `@returns_result` will wrap any exceptions thrown in an `Err` result.
But only those exceptions that are expected.
As noted above, if you do not explicitly specify exceptions to expect,
most runtime exceptions are expected by default.

```python
@returns_result()
def read_file() -> Result[str]:
    with open('/some/path/that/might/be/invalid') as f:
        return Ok(f.read())

result = read_file()
if result.is_ok():
    print(f'File content: {result.unwrap()}')
else:
    print(f'Error: {str(result.unwrap_err())}')
```

This will do as you expect.

You can also explicitly specify the exception to expect:
```python
@returns_result(expects=[FileNotFoundError])
def read_file() -> Result[str]:
    with open('/some/path/that/might/be/invalid') as f:
        return Ok(f.read())

result = read_file()
if result.is_ok():
    print(f'File content: {result.unwrap()}')
else:
    print(f'Error: {str(result.unwrap_err())}')
```
This also will do as you expect.

If fail to specify an exception that is raised as expected...
```python
from drresult import returns_result

@returns_result(expects=[IndexError, KeyError])
def read_file() -> Result[str]:
    with open('/this/path/is/invalid') as f:
        return Ok(f.read())

result = read_file()    # Panic!
```
.. it will be re-raised as `Panic`.

If you are feeling fancy, you can also do pattern matching:
```python
@returns_result(expects=[FileNotFoundError])
def read_file() -> Result[str]:
    with open('/this/path/is/invalid') as f:
        return Ok(f.read())

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

@returns_result(expects=[IndexError, KeyError, RuntimeError])
def retrieve_record_entry_backend(index: int, key: str) -> Result[str]:
    if key == 'baz':
        raise RuntimeError('Cannot process baz!')
    return Ok(data[index][key])

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


#### `unwrap_or_raise`

You can replicate the behaviour of Rust's `?`-operator with `unwrap_or_raise`:
```python
@returns_result()
def read_json(filename: str) -> Result[str]:
    with open(filename) as f:
        return Ok(json.loads(f.read()))

@returns_result()
def parse_file(filename: str) -> Result[dict]:
    content = read_file(filename).unwrap_or_raise()
    if not 'required_key' in content:
        raise KeyError('required_key')
    return Ok(content)
```
If the result is not `Ok`, `unwrap_or_raise()` will re-raise the contained exception.
Obviously, this will lead to an assertion if the contained exception is not expected.


#### `gather_result`

When you are interfacing with other modules that use exceptions,
you may want to react to certain exceptions being raised.
To avoid having to use `try/except` again,
you can transform exceptions from a part of your code to results:

```python
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
```

#### Printing the Stack Trace

If you want to format the exception stored in `Err`,
you can use `Err.__str__()` and `Err.trace()`.
The former will just provide the error message itself
where the latter will provide the entire stack trace.
The trace is filtered to remove all intermediate frames for internal functions.

Also, DrResult overrides the `expecthook` to filter the stack trace in case of panic.

#### `constructs_as_result`

If you have a class that might raise an error in its constructor,
you can mark it as `constructs_as_result`:

```python
@constructs_as_result
class Reader:
    def __init__(self, filename):
        with open(filename) as f:
            self.data = json.loads(f.read())
```
Creating an instance of this class will yield a `Result` that has to be unwrapped first.
```python
reader = Reader('/path/to/existing/file').unwrap() # Ok
reader = Reader('/invalid/path/to/non/existing/file').unwrap() # panic!
```

## Similar Projects

For a less extreme approach on Rust's result type, see:

* [https://github.com/rustedpy/result](https://github.com/rustedpy/result)
* [https://github.com/felixhammerl/resultify](https://github.com/felixhammerl/resultify)
