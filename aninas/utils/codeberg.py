from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, Optional

import httpx

from ..constant import CODEBERG, CODEBERG_KEY
from ..types import CodebergRepo, CodebergUser, CodebergPI, CodebergIC

client = httpx.AsyncClient(headers={"Authorization": f"token {CODEBERG_KEY}"})

__all__ = (
    "get_repo",
    "get_user",
    "get_pi"
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
    data = request.json()

    if "message" in data:
        return None
    
    return CodebergPI(data)

async def get_comment(user: str, repo: str, number: int, comment: int) -> Optional[CodebergIC]:
    request = await client.get(f"{CODEBERG}/repos/{user}/{repo}/issues/comments/{comment}")
    if request.status_code == 204: # NOTE: i don't really know why this happens
        return None

    data = request.json()

    if "message" in data:
        return None
    
    pi = await get_pi(user, repo, number)
    
    return CodebergIC(data, issue=pi)