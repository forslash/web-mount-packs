#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__version__ = (0, 0, 6, 4)
__license__ = "MIT <https://github.com/ChenyangGao/web-mount-packs/tree/main/python-cmdline/alist-strm-fuse/LICENSE>"

if __name__ == "__main__":
    from argparse import ArgumentParser, RawTextHelpFormatter

    parser = ArgumentParser(description="""\
基于 alist 和 fuse 的只读文件系统，支持罗列 strm
    1. Linux 要安装 libfuse：  https://github.com/libfuse/libfuse
    2. MacOSX 要安装 MacFUSE： https://github.com/osxfuse/osxfuse
    3. Windows 要安装 WinFsp： https://github.com/winfsp/winfsp

MIT licensed: https://github.com/ChenyangGao/web-mount-packs/tree/main/python-cmdline/alist-strm-fuse/LICENSE

⏰ 由于网盘对多线程访问的限制，请停用挂载目录的显示图标预览

访问源代码：
    - https://github.com/ChenyangGao/web-mount-packs/tree/main/python-wrap-alist-web-api/examples/strm-fuse

下面的选项 --ignore、--ignore-file、--strm、--strm-file 支持相同的配置语法。
    0. --strm、--strm-file 优先级高于 --ignore、--ignore-file，但前两者只针对文件（不针对目录），后两者都针对
    1. 从配置文件或字符串中，提取模式，执行模式匹配
    2. 模式匹配语法如下：
        1. 如果模式以反斜杠 \\ 开头，则跳过开头的 \\ 后，剩余的部分视为使用 gitignore 语法，对路径执行匹配（开头为 ! 时也不具有结果取反意义）
            - gitignore：https://git-scm.com/docs/gitignore#_pattern_format
        2. 如果模式以 ! 开头，则跳过开头的 ! 后，执行模式匹配，匹配成功即是失败，匹配失败即是成功，也就是结果取反
        3. 以 ! 开头的模式，优先级高于不以此开头的
        4. 如果启用扩展（-e 或 --extended-pattern-on）且模式以 =、^、$、:、;、,、<、>、|、~、-、% 之一开头
            - https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types

            0.     跳过下面的开头字符，剩余的部分称为模式字符串
            1. =   模式字符串等于被匹配字符串
            2. ^   模式字符串匹配被匹配字符串的开头
            3. $   模式字符串匹配被匹配字符串的结尾
            4. :   被匹配字符串里有等于此模式字符串的部分
            5. ;   对被匹配字符串按空白符号(空格、\\r、\\n、\\t、\\v、\\f 等)拆分，有一个部分等于此模式字符串
            6. ,   对被匹配字符串按逗号 , 拆分，有一个部分等于此字符串
            7. <   被匹配字符串里有一个单词（非标点符号、空白符号等组成的字符串）以此模式字符串开头
            8. >   被匹配字符串里有一个单词（非标点符号、空白符号等组成的字符串）以此模式字符串结尾
            9. |   被匹配字符串里有一个单词（非标点符号、空白符号等组成的字符串）等于此模式字符串
            10. ~  模式字符串是为正则表达式，被匹配字符串的一部分匹配此正则表达式
            11. -  模式字符串是为正则表达式，被匹配字符串的整体匹配此正则表达式
            12. %  模式字符串是为通配符表达式，被匹配字符串的整体匹配此通配符表达式
""", formatter_class=RawTextHelpFormatter)
    parser.add_argument("mount_point", nargs="?", help="挂载路径")
    parser.add_argument("-c", "--make-cache", help="""\
请提供一段代码，这段代码执行后，会产生一个名称为 cache 的值，将会被作为目录列表的缓存，如果代码执行成功却没有名为 cache 的值，则 cache 为 {}
例如提供的代码为

    from cachetools import TTLCache
    from sys import maxsize

    cache = TTLCache(maxsize, ttl=3600)

就会产生一个容量为 sys.maxsize 而 key 的存活时间为 1 小时的缓存

这个 cache 至少要求实现接口

    __getitem__, __setitem__

建议实现 collections.abc.MutableMapping 的接口，即以下接口

    __delitem__, __getitem__, __setitem__, __iter__, __len__

最好再实现析构方法

    __del__
""")
    parser.add_argument("-o", "--origin", default="http://localhost:5244", help="alist 服务器地址，默认 http://localhost:5244")
    parser.add_argument("-u", "--username", default="", help="用户名，默认为空")
    parser.add_argument("-p", "--password", default="", help="密码，默认为空")
    parser.add_argument("-m", "--max-readdir-workers", default=8, type=int, help="读取目录的文件列表的最大的并发线程数，默认值是 8，等于 0 则自动确定，小于 0 则不限制")
    parser.add_argument("--ignore", help="""\
接受配置，忽略其中罗列的文件和文件夹。
如果有多个，用空格分隔（如果文件名中包含空格，请用 \\ 转义）。""")
    parser.add_argument("--ignore-file", help="""\
接受一个配置文件路径，忽略其中罗列的文件和文件夹。
一行写一个配置，支持 # 开头作为注释。""")
    parser.add_argument("--strm", help="""\
接受配置，把罗列的文件显示为带 .strm 后缀的文件，打开后是链接。
优先级高于 --ignore 和 --ignore-file，如果有多个，用空格分隔（如果文件名中包含空格，请用 \\ 转义）。""")
    parser.add_argument("--strm-file", help="""\
接受一个配置文件路径，把罗列的文件显示为带 .strm 后缀的文件，打开后是链接。
优先级高于 --ignore 和 --ignore-file，如果有多个，用空格分隔（如果文件名中包含空格，请用 \\ 转义）。""")
    parser.add_argument("-e", "--extended-pattern-on", choices=("mime", "path", "name", "stem", "ext"), help="""\
启用扩展语法进行模式匹配
  - mime 针对文件名所对应的 mimetype （只针对文件，不会匹配目录）
  - path 针对文件路径（如果是目录，会有斜杠 / 作为后缀）
  - name 针对文件名（如果是目录，会有斜杠 / 作为后缀）
  - stem 针对文件名不含扩展名
  - ext  针对扩展名（不含前缀点号 .）
""")
    parser.add_argument(
        "-dn", "--direct-open-names", 
        help="为这些名字（忽略大小写）的程序直接打开链接，有多个时用空格分隔（如果文件名中包含空格，请用 \\ 转义）", 
    )
    parser.add_argument(
        "-de", "--direct-open-exes", 
        help="为这些路径的程序直接打开链接，有多个时用空格分隔（如果文件名中包含空格，请用 \\ 转义）", 
    )
    parser.add_argument("-v", "--version", action="store_true", help="输出版本号")
    parser.add_argument("-d", "--debug", action="store_true", help="调试模式，输出更多信息")
    parser.add_argument("-l", "--log-level", default=0, help=f"指定日志级别，可以是数字或名称，不传此参数则不输出日志，默认值: 0 (NOTSET)")
    parser.add_argument("-b", "--background", action="store_true", help="后台运行")
    parser.add_argument("-s", "--nothreads", action="store_true", help="不用多线程")
    parser.add_argument("--allow-other", action="store_true", help="允许 other 用户（也即不是 user 和 group）")
    #parser.add_argument("-i", "--iosize", type=int, help="每次读取的字节数")
    args = parser.parse_args()
    if args.version:
        print(*__version__, sep=".")
        raise SystemExit
    if not args.mount_point:
        parser.parse_args(["-h"])

    from sys import version_info

    if version_info < (3, 10):
        print("python 版本过低，请升级到至少 3.10")
        raise SystemExit(1)

try:
    from alist import __version__ as alist_version
    if alist_version < (0, 0, 9, 10):
        __import__("sys").modules.pop("alist")
        raise ImportError
    # pip install python-alist
    from alist import AlistFileSystem
    from alist.util.ignore import read_str, read_file, parse
    # pip install types-cachetools
    from cachetools import TTLCache
    # pip install fusepy
    from fuse import FUSE, FuseOSError, Operations, fuse_get_context
    # pip install psutil
    from psutil import Process
except ImportError:
    from subprocess import run
    from sys import executable
    run([executable, "-m", "pip", "install", "-U", "python-alist>=0.0.10", "cachetools", "fusepy", "psutil"], check=True)

    from alist import AlistFileSystem
    from alist.util.ignore import read_str, read_file, parse
    from cachetools import TTLCache
    from fuse import FUSE, FuseOSError, Operations, fuse_get_context # type: ignore
    from psutil import Process # type: ignore

from collections.abc import Callable, Container, MutableMapping
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial, update_wrapper
from errno import EACCES, EISDIR, ENOENT, EIO
from itertools import count
from mimetypes import guess_type
from posixpath import basename, dirname, join as joinpath, split as splitpath
from re import compile as re_compile
from stat import S_IFDIR, S_IFREG
from subprocess import run
from sys import maxsize
from threading import Event, Lock, Thread
from time import sleep, time
from types import MappingProxyType
from typing import cast, Any, BinaryIO, Final, Optional
from unicodedata import normalize
from weakref import WeakKeyDictionary, WeakValueDictionary
from zipfile import ZipFile, Path as ZipPath, BadZipFile

from util.log import logger


CRE_PAT_IN_STR: Final = re_compile(r"[^\\ ]*(?:\\(?s:.)[^\\ ]*)*")
_EXTRA = MappingProxyType({"instance": __name__})

if not hasattr(ThreadPoolExecutor, "__del__"):
    setattr(ThreadPoolExecutor, "__del__", lambda self, /: self.shutdown(cancel_futures=True))


def _get_process():
    pid = fuse_get_context()[-1]
    if pid <= 0:
        return "UNDETERMINED"
    return str(Process(pid))
PROCESS_STR = type("ProcessStr", (), {"__str__": staticmethod(_get_process)})()


def update_readdir_later(
    self, 
    executor: Optional[ThreadPoolExecutor] = None, 
    refresh_min_interval: int | float = 10, 
):
    readdir = type(self).readdir
    refresh_freq: MutableMapping = TTLCache(maxsize, ttl=refresh_min_interval)
    event_pool: dict[str, Event] = {}
    lock = Lock()
    def run_update(path, fh, /, do_refresh=True):
        with lock:
            try:
                evt = event_pool[path]
                wait_event = True
            except KeyError:
                evt = event_pool[path] = Event()
                wait_event = False
        if wait_event:
            if do_refresh:
                return
            evt.wait()
            return [".", "..", *self.cache[normalize("NFC", path)]]
        else:
            try:
                return readdir(self, path, fh)
            finally:
                event_pool.pop(path, None)
                evt.set()
    def wrapper(path, fh=0):
        while True:
            try:
                cache = self.cache[normalize("NFC", path)]
            except KeyError:
                if executor is None:
                    return run_update(path, fh)
                else:
                    future = executor.submit(run_update, path, fh)
                    return future.result()
            else:
                try:
                    if path not in refresh_freq:
                        refresh_freq[path] = None
                        if executor is None:
                            Thread(target=run_update, args=(path, fh)).start()
                        else:
                            executor.submit(run_update, path, fh)
                    return [".", "..", *cache]
                except BaseException as e:
                    self._log(
                        logging.ERROR, 
                        "can't start new thread for path: \x1b[4;34m%s\x1b[0m\n  |_ \x1b[1;4;31m%s\x1b[0m: %s", 
                        path, type(e).__qualname__, e, 
                    )
                    raise FuseOSError(EIO) from e
    return update_wrapper(wrapper, readdir)


# Learn: https://www.stavros.io/posts/python-fuse-filesystem/
class AlistFuseOperations(Operations):

    def __init__(
        self, 
        /, 
        origin: str = "http://localhost:5244", 
        username: str = "", 
        password: str = "", 
        cache: Optional[MutableMapping] = None, 
        predicate: Optional[Callable[[str], bool]] = None, 
        strm_predicate: Optional[Callable[[str], bool]] = None, 
        max_readdir_workers: int = -1, 
        direct_open_names: Optional[Callable[[str], bool]] = None, 
        direct_open_exes: Optional[Callable[[str], bool]] = None, 
    ):
        self.__finalizer__: list[Callable] = []
        self._log = partial(logger.log, extra={"instance": repr(self)})

        self.fs = AlistFileSystem.login(origin, username, password)
        self.predicate = predicate
        self.strm_predicate = strm_predicate
        register = self.register_finalize = self.__finalizer__.append
        self.direct_open_names = direct_open_names
        self.direct_open_exes = direct_open_exes

        # id generator for file handler
        self._next_fh: Callable[[], int] = count(1).__next__
        # cache `readdir` pulled file attribute map
        if cache is None:
            cache = {}
        self.cache = cache
        # cache all opened files (except in zipfile)
        self._fh_to_file: dict[int, tuple[BinaryIO, bytes]] = {}
        def close_all():
            popitem = self._fh_to_file.popitem
            while True:
                try:
                    _, (file, _) = popitem()
                    if file is not None:
                        file.close()
                except KeyError:
                    break
                except:
                    pass
        register(close_all)
        # multi threaded directory reading control
        executor: Optional[ThreadPoolExecutor]
        if max_readdir_workers < 0:
            executor = None
        elif max_readdir_workers == 0:
            executor = ThreadPoolExecutor(None)
        else:
            executor = ThreadPoolExecutor(max_readdir_workers)
        self.__dict__["readdir"] = update_readdir_later(self, executor=executor)
        if executor is not None:
            register(partial(executor.shutdown, cancel_futures=True))
        self.normpath_map = {}

    def __del__(self, /):
        self.close()

    def close(self, /):
        for func in self.__finalizer__:
            try:
                func()
            except BaseException as e:
                self._log(logging.ERROR, "failed to finalize with %r", func)

    def getattr(self, /, path: str, fh: int = 0, _rootattr={"st_mode": S_IFDIR | 0o555}) -> dict:
        self._log(logging.DEBUG, "getattr(path=\x1b[4;34m%r\x1b[0m, fh=%r) by \x1b[3;4m%s\x1b[0m", path, fh, PROCESS_STR)
        if path == "/":
            return _rootattr
        dir_, name = splitpath(normalize("NFC", path))
        try:
            dird = self.cache[dir_]
        except KeyError:
            try:
                self.readdir(dir_)
                dird = self.cache[dir_]
            except BaseException as e:
                self._log(
                    logging.WARNING, 
                    "file not found: \x1b[4;34m%s\x1b[0m, since readdir failed: \x1b[4;34m%s\x1b[0m\n  |_ \x1b[1;4;31m%s\x1b[0m: %s", 
                    path, dir_, type(e).__qualname__, e, 
                )
                raise FuseOSError(EIO) from e
        try:
            return dird[name]
        except KeyError as e:
            self._log(
                logging.WARNING, 
                "file not found: \x1b[4;34m%s\x1b[0m\n  |_ \x1b[1;4;31m%s\x1b[0m: %s", 
                path, type(e).__qualname__, e, 
            )
            raise FuseOSError(ENOENT) from e

    def open(self, /, path: str, flags: int = 0) -> int:
        self._log(logging.INFO, "open(path=\x1b[4;34m%r\x1b[0m, flags=%r) by \x1b[3;4m%s\x1b[0m", path, flags, PROCESS_STR)
        pid = fuse_get_context()[-1]
        if pid > 0:
            process = Process(pid)
            exe = process.exe()
            if (
                self.direct_open_names is not None and self.direct_open_names(process.name().lower()) or
                self.direct_open_exes is not None and self.direct_open_exes(exe)
            ):
                process.kill()
                def push():
                    sleep(.01)
                    run([exe, self.fs.get_url(path)])
                Thread(target=push).start()
                return 0
        return self._next_fh()

    def _open(self, path: str, /, start: int = 0):
        attr = self.getattr(path)
        path = self.normpath_map.get(normalize("NFC", path), path)
        if attr.get("_data") is not None:
            return None, attr["_data"]
        if attr["st_size"] <= 2048:
            return None, self.fs.as_path(path).read_bytes()
        file = cast(BinaryIO, self.fs.as_path(path).open("rb"))
        if start == 0:
            # cache 2048 in bytes (2 KB)
            preread = file.read(2048)
        else:
            preread = b""
        return file, preread

    def read(self, /, path: str, size: int, offset: int, fh: int = 0) -> bytes:
        self._log(logging.DEBUG, "read(path=\x1b[4;34m%r\x1b[0m, size=%r, offset=%r, fh=%r) by \x1b[3;4m%s\x1b[0m", path, size, offset, fh, PROCESS_STR)
        if not fh:
            return b""
        try:
            try:
                file, preread = self._fh_to_file[fh]
            except KeyError:
                file, preread = self._fh_to_file[fh] = self._open(path, offset)
            cache_size = len(preread)
            if offset < cache_size:
                if offset + size <= cache_size:
                    return preread[offset:offset+size]
                elif file is not None:
                    file.seek(cache_size)
                    return preread[offset:] + file.read(offset+size-cache_size)
            file.seek(offset)
            return file.read(size)
        except BaseException as e:
            self._log(
                logging.ERROR, 
                "can't read file: \x1b[4;34m%s\x1b[0m\n  |_ \x1b[1;4;31m%s\x1b[0m: %s", 
                path, type(e).__qualname__, e, 
            )
            raise FuseOSError(EIO) from e

    def readdir(self, /, path: str, fh: int = 0) -> list[str]:
        self._log(logging.DEBUG, "readdir(path=\x1b[4;34m%r\x1b[0m, fh=%r) by \x1b[3;4m%s\x1b[0m", path, fh, PROCESS_STR)
        predicate = self.predicate
        strm_predicate = self.strm_predicate
        cache = {}
        path = normalize("NFC", path)
        realpath = self.normpath_map.get(path, path)
        try:
            for pathobj in self.fs.listdir_path(realpath):
                name    = pathobj.name
                subpath = pathobj.path
                isdir   = pathobj.is_dir()
                data = None
                if not isdir and strm_predicate and strm_predicate(subpath):
                    data = pathobj.url.encode("latin-1")
                    size = len(data)
                    name += ".strm"
                elif predicate and not predicate(subpath + "/"[:isdir]):
                    continue
                elif isdir:
                    size = 0
                else:
                    size = int(pathobj.get("size", 0))
                normname = normalize("NFC", name)
                cache[normname] = dict(
                    st_mode=(S_IFDIR if isdir else S_IFREG) | 0o555, 
                    st_size=size, 
                    st_ctime=pathobj["ctime"], 
                    st_mtime=pathobj["mtime"], 
                    st_atime=pathobj["atime"], 
                    _data=data, 
                )
                normsubpath = joinpath(path, normname)
                if normsubpath != normalize("NFD", normsubpath):
                    self.normpath_map[normsubpath] = joinpath(realpath, name)
            self.cache[path] = cache
            return [".", "..", *cache]
        except BaseException as e:
            self._log(
                logging.ERROR, 
                "can't readdir: \x1b[4;34m%s\x1b[0m\n  |_ \x1b[1;4;31m%s\x1b[0m: %s", 
                path, type(e).__qualname__, e, 
            )
            raise FuseOSError(EIO) from e

    def release(self, /, path: str, fh: int = 0):
        self._log(logging.DEBUG, "release(path=\x1b[4;34m%r\x1b[0m, fh=%r) by \x1b[3;4m%s\x1b[0m", path, fh, PROCESS_STR)
        if not fh:
            return
        try:
            file, _ = self._fh_to_file.pop(fh)
            if file is not None:
                file.close()
        except KeyError:
            pass
        except BaseException as e:
            self._log(
                logging.ERROR, 
                "can't release file: \x1b[4;34m%s\x1b[0m\n  |_ \x1b[1;4;31m%s\x1b[0m: %s", 
                path, type(e).__qualname__, e, 
            )
            raise FuseOSError(EIO) from e


if __name__ == "__main__":
    import logging

    log_level = args.log_level
    if isinstance(log_level, str):
        try:
            log_level = int(log_level)
        except ValueError:
            log_level = getattr(logging, log_level.upper(), logging.NOTSET)
    logger.setLevel(log_level)

    ls: list[str] = []
    strm_predicate = None
    if args.strm:
        ls.extend(read_str(args.strm))
    if args.strm_file:
        try:
            ls.extend(read_file(open(args.strm_file, encoding="utf-8")))
        except OSError:
            logger.exception("can't read file: %r", args.strm_file, extra=_EXTRA)
    if ls:
        strm_predicate = parse(ls, extended_type=args.extended_pattern_on)

    ls = []
    predicate = None
    if args.ignore:
        ls.extend(read_str(args.ignore))
    if args.ignore_file:
        try:
            ls.extend(read_file(open(args.ignore_file, encoding="utf-8")))
        except OSError:
            logger.exception("can't read file: %r", args.ignore_file, extra=_EXTRA)
    if ls:
        ignore = parse(ls, extended_type=args.extended_pattern_on)
        if ignore:
            predicate = lambda p: not ignore(p)

    cache = None
    if args.make_cache:
        from textwrap import dedent
        code = dedent(args.make_cache)
        ns: dict = {}
        exec(code, ns)
        cache = ns.get("cache")

    direct_open_names = None
    if args.direct_open_names:
        names = {n.replace(r"\ ", " ") for n in CRE_PAT_IN_STR.findall(args.direct_open_names) if n}
        if names:
            direct_open_names = names.__contains__

    direct_open_exes = None
    if args.direct_open_exes:
        exes = {e.replace(r"\ ", " ") for e in CRE_PAT_IN_STR.findall(args.direct_open_exes) if n}
        if names:
            direct_open_exes = exes.__contains__

    print("\n    👋 Welcome to use alist fuse and strm 👏\n")
    # https://code.google.com/archive/p/macfuse/wikis/OPTIONS.wiki
    fuse = FUSE(
        AlistFuseOperations(
            args.origin, 
            args.username, 
            args.password, 
            cache=cache, 
            predicate=predicate, 
            strm_predicate=strm_predicate, 
            max_readdir_workers=args.max_readdir_workers, 
            direct_open_names=direct_open_names, 
            direct_open_exes=direct_open_exes, 
        ),
        args.mount_point, 
        ro=True, 
        allow_other=args.allow_other, 
        foreground=not args.background, 
        nothreads=args.nothreads, 
        debug=args.debug, 
    )
