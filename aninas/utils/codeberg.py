from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..database import Redis
    from typing import Optional, Tuple

import httpx
import textwrap
import base64

from ..constant import CODEBERG_KEY

from .types.codeberg.repository import Repository
from .types.codeberg.comment import Comment
from .types.codeberg.issue import Issue
from .types.codeberg.user import User

class Codeberg:
    def __init__(self, redis: Redis):
        self.client = httpx.AsyncClient(
            headers = {
                "Authorization": f"token {CODEBERG_KEY}", 
                "User-Agent": "Aninas"
            }
        )

        self.redis = redis
        self.api_url = "https://codeberg.org/api/v1"
    
    async def get_repository(self, user: str, repo: str) -> Optional[Repository]:
        user_repo = f"{user}/{repo}"

        cache = await self.redis.get(f"cb_{user_repo}")

        if cache:
            return Repository(cache)
        
        repos = await self.client.get(f"{self.api_url}/repos/{user_repo}")
        json = repos.json()

        if "message" in json:
            raise CodebergError(json["message"])

        await self.redis.set(f"cb_{user_repo}", json, 3600)

        return Repository(json)

    async def get_user(self, user: str) -> Optional[User]:
        cache = await self.redis.get(f"cb_{user}")

        if cache:
            return User(cache)

        users = await self.client.get(f"{self.api_url}/users/{user}")
        json = users.json()

        if "message" in json:
            raise CodebergError(json["message"])

        orgs = await self.client.get(f"{self.api_url}/users/{user}/orgs")
        repos = await self.client.get(f"{self.api_url}/users/{user}/repos")

        json["orgs"] = orgs.json()
        json["repos"] = repos.json()

        await self.redis.set(f"cb_{user}", json, 3600)

        return User(json)
    
    async def get_comment(self, user_repo: str, number: int, comment_id: int) -> Optional[Comment]:
        cache = await self.redis.get(f"cb_{comment_id}")

        if cache:
            return Comment(cache)
    
        comment = await self.client.get(f"{self.api_url}/repos/{user_repo}/issues/comments/{comment_id}")
        
        json = comment.json()

        if comment.status_code == 204 or "message" in json:
            return None
        
        issue = await self.client.get(f"{self.api_url}/repos/{user_repo}/issues/{number}")

        json["issue"] = issue.json()
        json["id"] = number

        await self.redis.set(f"cb_{comment_id}", json)

        return Comment(json)
    
    async def get_issue(self, user_repo: str, issue_id: int) -> Optional[Issue]:
        cache = await self.redis.get(f"cb_{user_repo}_{issue_id}")

        if cache:
            return Issue(cache)
    
        comment = await self.client.get(f"{self.api_url}/repos/{user_repo}/issues/{issue_id}")
        pr = await self.client.get(f"{self.api_url}/repos/{user_repo}/pulls/{issue_id}")

        json = comment.json()
        pr_json = pr.json()

        if "message" in json:
            return None
        
        if "message" in pr_json:
            pr_json = None
        
        json["pr"] = pr_json

        await self.redis.set(f"cb_{user_repo}_{issue_id}", json)

        return Issue(json)
    
    async def get_code(self, repo: str, path: str, start_line: int, end_line: Optional[int]) -> Optional[str]:
        ref, file_path = await self.__get_ref(repo, path)

        if ref is None:
            return None

        request = await self.client.get(f"{self.api_url}/repos/{repo}/contents/{file_path}?ref={ref}")
        data = request.json()

        if "message" in data:
            return None
        
        content = base64.b64decode(data["content"]).decode()

        return self.__code_snippet(file_path, content, start_line, end_line)
        
    async def __get_ref(self, repo: str, path: str) -> Optional[Tuple[str, str]]:
        _, rest = path.split("/", 1)    

        request = await self.client.get(f"{self.api_url}/repos/{repo}/branches")
        data = request.json()

        if "message" in data:
            return None

        ref, file_path = rest.split("/", 1)

        for possible_ref in data:
            if rest.startswith(possible_ref["name"] + "/"):
                ref = possible_ref["name"]
                file_path = rest[len(ref) + 1 :]
                break

        file_path = file_path.split("?")[0]

        return ref, file_path

    # https://github.com/onerandomusername/monty-python/blob/main/monty/exts/info/codesnippets.py#L232
    def __code_snippet(self, path: str, data: str, start_line: int, end_line: Optional[int]) -> Optional[str]:
        language = path.split("/")[-1].split(".")[-1]
        is_valid_language = language.isalnum()

        start_line = int(start_line)

        if end_line is None:
            end_line = start_line

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

class CodebergError(Exception):
    pass