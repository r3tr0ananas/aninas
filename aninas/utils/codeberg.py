from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, Optional

import httpx
import base64
import textwrap

from ..constant import CODEBERG, CODEBERG_KEY
from ..types import CodebergRepo, CodebergUser, CodebergPI, CodebergIC

client = httpx.AsyncClient(headers={"Authorization": f"token {CODEBERG_KEY}"})

__all__ = (
    "get_repo",
    "get_user",
    "get_pi",
    "get_file"
)

async def get_repo(user: str, repo: str) -> CodebergRepo:
    request = await client.get(f"{CODEBERG}/repos/{user}/{repo}")
    data = request.json()

    if "errors" in data:
        return data["errors"][0]

    data = CodebergRepo(data)

    return data

async def get_user(user: str) -> Tuple[CodebergUser, int] | str:
    request = await client.get(f"{CODEBERG}/users/{user}")
    data = request.json()

    if "message" in data:
        error_message = data["message"]
        return error_message, None

    request_orgs = await client.get(f"{CODEBERG}/users/{user}/orgs")
    request_repos = await client.get(f"{CODEBERG}/users/{user}/repos")

    orgs_data = request_orgs.json()
    repos_data = request_repos.json()

    return CodebergUser(data = data, orgs = orgs_data), len(repos_data)

async def get_pi(user: str, repo: str, number: int) -> Optional[CodebergPI]:
    request = await client.get(f"{CODEBERG}/repos/{user}/{repo}/issues/{number}")
    pr_data = None

    if request.is_error:
        return None

    data = request.json()

    if data["html_url"].split("/")[5]:
        pr_request = await client.get(f"{CODEBERG}/repos/{user}/{repo}/pulls/{number}")
        pr_data = pr_request.json()

    if "message" in data:
        return None
    
    if "message" in pr_data:
        pr_data = None

    return CodebergPI(data=data, pr_data=pr_data)

async def get_comment(user: str, repo: str, number: int, comment: int) -> Optional[CodebergIC]:
    request = await client.get(f"{CODEBERG}/repos/{user}/{repo}/issues/comments/{comment}")
    if request.status_code == 204: # NOTE: i don't really know why this happens
        return None

    data = request.json()

    if "message" in data:
        return None
    
    pi = await get_pi(user, repo, number)
    
    return CodebergIC(data, issue=pi)

async def get_file(repo: str, path: int, start_line: int, end_line: int) -> Optional[str]:
    ref, file_path = await _get_ref(repo, path)

    if ref is None:
        return None

    request = await client.get(f"{CODEBERG}/repos/{repo}/contents/{file_path}?ref={ref}")
    data = request.json()

    if "message" in data:
        return None
    
    content = base64.b64decode(data["content"]).decode()

    return _code_snippet(file_path, content, start_line, end_line)

async def _get_ref(repo: str, path: str) -> Optional[Tuple[str, str]]:
    type, rest = path.split("/", 1)

    request = await client.get(f"{CODEBERG}/repos/{repo}/branches")
    data = request.json()

    if "message" in data:
        return None
    
    ref, file_path = rest.split("/", 1)
        
    for possible_ref in data:
        if path.startswith(possible_ref["name"] + "/"):
            ref = possible_ref["name"]
            file_path = path[len(ref) + 1 :]
            break

    return ref, file_path

# https://github.com/onerandomusername/monty-python/blob/main/monty/exts/info/codesnippets.py#L232
def _code_snippet(path: str, data: str, start_line: int, end_line: int) -> Optional[str]:
    language = path.split("/")[-1].split(".")[-1]
    is_valid_language = language.isalnum()

    start_line = int(start_line)
    end_line = int(end_line)

    if is_valid_language:
        language = "py" if language == "pyi" else language
    else:
        language = ""

    split_lines = data.splitlines()

    if start_line > len(split_lines) or end_line < 1:
        return None
    
    start_line = max(1, start_line)
    end_line = min(len(split_lines), end_line)

    required = "\n".join(split_lines[start_line - 1 : end_line])
    required = textwrap.dedent(required).rstrip().replace("`", "`\u200b")

    if "`" in path:
        if path.startswith("`"):
            path = "\u200b" + path
        path = path.replace("`", "`\u200b")

    if start_line == end_line:
        ret = f"`{path}` line {start_line}\n"
    else:
        ret = f"`{path}` lines {start_line} to {end_line}\n"

    if len(required) != 0:
        return f"{ret}```{language}\n{required}\n```"

    return f"{ret}```\n```"