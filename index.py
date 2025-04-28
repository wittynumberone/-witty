import discord

from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Modal, TextInput, Button, View, Select
from datetime import datetime, timedelta, timezone
import os
import asyncio
import json
import logging
import json
from datetime import datetime
from discord.utils import get

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_config(file_path):
    with open(file_path, "r") as config_file:
        return json.load(config_file)

config=load_config("config.json")



TOKEN = config["token"]

def get_categories():
    try:
        with open('close-command-category.json', 'r') as f:
            data = json.load(f)
        return data['categories']
    except FileNotFoundError:
        logging.error("Il file close-command-category.json non è stato trovato.")
        return []
    except json.JSONDecodeError:
        logging.error("Errore nella lettura del file JSON.")
        return []




@bot.tree.command(name="role-add")
@app_commands.describe(user="Assegna un ruolo a un utente", role="Ruolo da aggiungere")
async def add(interaction: discord.Interaction,user: discord.Member, role: discord.Role): 
    textCanale = interaction.channel
    canaleid = 1362807999781015712
    canale = interaction.guild.get_channel(canaleid)

    canaleLogId = 1366053648345595964
    canaleLog = interaction.guild.get_channel(canaleLogId)

    if textCanale.id ==canale.id:
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("[❌] Non posso assegnare questo ruolo (è troppo alto).", ephemeral=True)
            return

        if interaction.guild.me.guild_permissions.manage_roles:
            try:
                await user.add_roles(role)
                await interaction.response.send_message(f"[✅] Ruolo **{role.mention}** assegnato a **{user.mention}**!", ephemeral=True)

                await canaleLog.send(f"[📜] {interaction.user.mention} ha aggiunto il ruolo {role.mention} a {user.mention}")
            except Exception as e:
                await interaction.response.send_message(f"[❌] Errore nell'assegnazione del ruolo: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("[❌] Non ho il permesso di gestire i ruoli.", ephemeral=True)
    else:
        await interaction.response.send_message("[❌] Non puoi eseguire questo comando qui.", ephemeral=True)

@bot.tree.command(name="role-remove")
@app_commands.describe(user="Rimuovi un ruolo a un utente", role="Ruolo da rimuovere")
async def add(interaction: discord.Interaction,user: discord.Member, role: discord.Role): 
    textCanale = interaction.channel
    canaleId = 1362807999781015712
    canale = interaction.guild.get_channel(canaleId)

    canaleLogId = 1366053648345595964
    canaleLog = interaction.guild.get_channel(canaleLogId)

    if textCanale.id ==canale.id:
        if role >= interaction.guild.me.top_role:
            await interaction.response.send_message("[❌] Non posso rimuovere questo ruolo (è troppo alto).", ephemeral=True)
            return

        if interaction.guild.me.guild_permissions.manage_roles and role in user.roles:
            try:
                await user.remove_roles(role)
                await interaction.response.send_message(f"[✅] Ruolo {role.mention} rimosso a {user.mention}!", ephemeral=True)

                await canaleLog.send(f"[📜] {interaction.user.mention} ha rimosso il ruolo {role.mention} a {user.mention}")
            except Exception as e:
                await interaction.response.send_message(f"[❌] Errore nell'assegnazione del ruolo: {e}", ephemeral=True)
        else:
            await interaction.response.send_message(f"[❌] Non ho il permesso di gestire i ruoli oppure hai provato a togliere un ruolo che {user.mention} non ha.", ephemeral=True)
    else:
        await interaction.response.send_message("[❌] Non puoi eseguire questo comando qui.", ephemeral=True)

@bot.event
async def on_ready():
    print("")
    print(f'{bot.user} has connected to Discord!')
    print(f"The ping of the bot is {bot.latency} ms")
    await bot.tree.sync()





bot.run(TOKEN)