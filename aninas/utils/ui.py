from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

import disnake

class Delete(disnake.ui.View):
    def __init__(self, author: disnake.User):
        self.author = author

        super().__init__(timeout=None)

    @disnake.ui.button(emoji="🗑️", style=disnake.ButtonStyle.red)
    async def delete(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.author.id == inter.author.id or inter.permissions.manage_messages:
            await inter.response.defer()
            await inter.delete_original_response()
        else:
            await inter.response.send_message("You are not allowed to press this button", ephemeral=True)

class ShowLess(Delete):
    def __init__(self, data, author: disnake.User, make_embed: Callable):
        super().__init__(author = author)

        self.data = data
        self.make_embed = make_embed

    @disnake.ui.button(emoji="⬆️", label="Show less", style=disnake.ButtonStyle.green)
    async def show_less(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.author.id == inter.author.id or inter.permissions.manage_messages:
            embed = self.make_embed(self.data, True)

            await inter.response.edit_message(embed=embed, view=ShowMore(self.data, self.author, self.make_embed))
        else:
            await inter.response.send_message("You are not allowed to press this button", ephemeral=True)
    

class ShowMore(Delete):
    def __init__(self, data, author: disnake.User, make_embed: Callable):
        super().__init__(author=author)

        self.data = data
        self.make_embed = make_embed
    
    @disnake.ui.button(emoji="⬇️", label="Show more", style=disnake.ButtonStyle.green)
    async def show_more(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if self.author.id == inter.author.id or inter.permissions.manage_messages:  
            embed = self.make_embed(self.data)

            await inter.response.edit_message(embed=embed, view=ShowLess(self.data, self.author, self.make_embed))
