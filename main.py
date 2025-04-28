import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get
import json
import os
import random

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_config(file_path):
    with open(file_path, "r") as config_file:
        return json.load(config_file)

def load_user_roles(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_user_roles(file_path, user_roles):
    try:
        with open(file_path, "w") as f:
            json.dump(user_roles, f, indent=4)
        print("File user_roles.json salvato con successo.")
    except Exception as e:
        print(f"Errore nel salvataggio di user_roles.json: {e}")

config = load_config("config.json")
TOKEN = config["token"]
user_roles = load_user_roles("user_roles.json")

def load_user_xp(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

def save_user_xp(file_path, user_xp):
    try:
        with open(file_path, "w") as f:
            json.dump(user_xp, f, indent=4)
        print("File user_xp.json salvato con successo.")
    except Exception as e:
        print(f"Errore nel salvataggio di user_xp.json: {e}")

user_xp = load_user_xp("user_xp.json")

def calculate_level(xp):
    level = 1
    required_xp = 100
    while xp >= required_xp:
        xp -= required_xp
        level += 1
        required_xp = int(required_xp * 1.5)
    return level

async def check_channel(interaction, canale_id):
    canale = interaction.guild.get_channel(canale_id)
    if interaction.channel.id != canale.id:
        await interaction.response.send_message("[❌] Non puoi eseguire questo comando qui.", ephemeral=True)
        return False
    return True

@bot.tree.command(name="role-add", description="Aggiungi un ruolo ad un utente specifico")
@app_commands.describe(user="Assegna un ruolo a un utente", role="Ruolo da aggiungere")
async def add(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    canale_id = [1362807999781015712, 1264205848549396532]
    canale_log_id = 1366053648345595964
    canale_log = interaction.guild.get_channel(canale_log_id)

    if not await check_channel(interaction, canale_id):
        return

    allowed_roles = [
        role.id for role in interaction.user.roles if role.id in role_permissions.get(role.id, [])
    ]

    if role.id not in allowed_roles:
        await interaction.response.send_message("[❌] Non hai il permesso di assegnare questo ruolo.", ephemeral=True)
        return

    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message("[❌] Non posso assegnare questo ruolo (è troppo alto).", ephemeral=True)
        return

    if interaction.guild.me.guild_permissions.manage_roles:
        try:
            await user.add_roles(role)
            await interaction.response.send_message(f"[✅] Ruolo **{role.mention}** assegnato a **{user.mention}**!", ephemeral=True)
            await canale_log.send(f"[📜] {interaction.user.mention} ha aggiunto il ruolo {role.mention} a {user.mention}")
        except Exception as e:
            await interaction.response.send_message(f"[❌] Errore nell'assegnazione del ruolo: {e}", ephemeral=True)
    else:
        await interaction.response.send_message("[❌] Non ho il permesso di gestire i ruoli.", ephemeral=True)

@bot.tree.command(name="role-remove", description="Rimuovi un ruolo ad un utente specifico")
@app_commands.describe(user="Rimuovi un ruolo a un utente", role="Ruolo da rimuovere")
async def remove(interaction: discord.Interaction, user: discord.Member, role: discord.Role):
    canale_id = 1362807999781015712
    canale_log_id = 1366053648345595964
    canale_log = interaction.guild.get_channel(canale_log_id)

    if not await check_channel(interaction, canale_id):
        return

    allowed_roles = [
        role.id for role in interaction.user.roles if role.id in role_permissions.get(role.id, [])
    ]

    if role.id not in allowed_roles:
        await interaction.response.send_message("[❌] Non hai il permesso di rimuovere questo ruolo.", ephemeral=True)
        return

    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message("[❌] Non posso rimuovere questo ruolo (è troppo alto).", ephemeral=True)
        return

    if interaction.guild.me.guild_permissions.manage_roles and role in user.roles:
        try:
            await user.remove_roles(role)
            await interaction.response.send_message(f"[✅] Ruolo **{role.mention}** rimosso da **{user.mention}**!", ephemeral=True)
            await canale_log.send(f"[📜] {interaction.user.mention} ha rimosso il ruolo {role.mention} a {user.mention}")
        except Exception as e:
            await interaction.response.send_message(f"[❌] Errore nel rimuovere il ruolo: {e}", ephemeral=True)
    else:
        await interaction.response.send_message(f"[❌] Non posso rimuovere un ruolo che {user.mention} non ha.", ephemeral=True)

AUTHORIZED_CHANNELS = [1313883609639161958, 1264205848549396532]

@bot.tree.command(name="clear", description="Cancella un numero specificato di messaggi nel canale.")
@app_commands.describe(amount="Numero di messaggi da cancellare")
async def clear(interaction: discord.Interaction, amount: int):
    if interaction.channel.id not in AUTHORIZED_CHANNELS:
        return await interaction.response.send_message("[❌] Questo comando non è autorizzato in questo canale.", ephemeral=True)

    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("[❌] Non hai il permesso di gestire i messaggi.", ephemeral=True)

    amount = min(amount, 100)

    deleted = await interaction.channel.purge(limit=amount)
    
    await interaction.response.send_message(f"[✅] Ho cancellato {len(deleted)} messaggi.", ephemeral=True)

@bot.event
async def on_member_join(member):
    welcome_channel_id = config.get("welcome_channel_id")
    if welcome_channel_id:
        channel = member.guild.get_channel(welcome_channel_id)
        if channel:
            await channel.send(f"Benvenuto {member.mention}! Siamo felici di averti qui!")
    
    if member.id in user_roles:
        roles_to_add = user_roles[member.id]
        role_objects = [get(member.guild.roles, id=role_id) for role_id in roles_to_add]
        role_objects = [role for role in role_objects if role is not None]

        if role_objects:
            try:
                await member.add_roles(*role_objects)
                print(f"Ruoli ripristinati per {member.name}")
            except Exception as e:
                print(f"Errore nel ripristinare i ruoli per {member.name}: {e}")

@bot.event
async def on_member_remove(member):
    user_roles[member.id] = [role.id for role in member.roles if role != member.guild.default_role]
    print(f"Ruoli da salvare per {member.name}: {user_roles[member.id]}")
    save_user_roles("user_roles.json", user_roles)
    print(f"Ruoli di {member.name} salvati.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    if user_id not in user_xp:
        user_xp[user_id] = {'xp': 0}

    user_xp[user_id]['xp'] += 1
    save_user_xp("user_xp.json", user_xp)

@bot.tree.command(name="level", description="Mostra il livello e l'XP dell'utente.")
@app_commands.describe(user="L'utente di cui mostrare il livello")
async def level(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    user_id = str(user.id)

    if user_id in user_xp:
        xp = user_xp[user_id]['xp']
    else:
        xp = 0

    current_level = calculate_level(xp)
    await interaction.response.send_message(f"{user.mention}, sei al livello {current_level} con {xp} XP!")

@bot.tree.command(name="mute", description="Esegui questo comando per mutare uno specifico utente")
@app_commands.describe(user="L'utente da mutare")
async def mute(interaction: discord.Interaction, user: discord.Member):
    mute_role = get(interaction.guild.roles, name="Muted")
    if not mute_role:
        await interaction.response.send_message("[❌] Ruolo 'Muted' non trovato.", ephemeral=True)
        return

    await user.add_roles(mute_role)
    await interaction.response.send_message(f"[✅] {user.mention} è stato mutato.", ephemeral=True)

@bot.tree.command(name="unmute", description="Esegui questo comando per smutare uno specifico utente")
@app_commands.describe(user="L'utente da smutare")
async def unmute(interaction: discord.Interaction, user: discord.Member):
    mute_role = get(interaction.guild.roles, name="Muted")
    if not mute_role:
        await interaction.response.send_message("[❌] Ruolo 'Muted' non trovato.", ephemeral=True)
        return

    await user.remove_roles(mute_role)
    await interaction.response.send_message(f"[✅] {user.mention} è stato riattivato.", ephemeral=True)

@bot.tree.command(name="poll", description="Crea un sondaggio.")
@app_commands.describe(question="La domanda del sondaggio", options="Opzioni del sondaggio separate da virgole")
async def poll(interaction: discord.Interaction, question: str, options: str):
    option_list = [option.strip() for option in options.split(',')]
    
    if len(option_list) < 2:
        await interaction.response.send_message("[❌] Devi fornire almeno due opzioni!", ephemeral=True)
        return

    poll_message = await interaction.channel.send(f"**{question}**\n" + "\n".join([f"{i + 1}. {option}" for i, option in enumerate(option_list)]))

    for i in range(len(option_list)):
        if i < 9:
            await poll_message.add_reaction(f"{i + 1}\u20E3")
        elif i == 9:
            await poll_message.add_reaction("🔟")

@bot.tree.command(name="avatar", description="Visualizza l'avatar di un utente.")
@app_commands.describe(user="L'utente di cui mostrare l'avatar")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    canale_id_avatar = 1313883609639161958
    if not await check_channel(interaction, canale_id_avatar):
        return

    user = user or interaction.user
    embed = discord.Embed(title=f"Avatar di {user.display_name}")
    embed.set_image(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Esegui questo comando per vedere info del server")
async def server_info(interaction: discord.Interaction):
    canale_id_serverinfo = 1313883609639161958
    if not await check_channel(interaction, canale_id_serverinfo):
        return

    guild = interaction.guild
    embed = discord.Embed(title=f"Informazioni su {guild.name}", color=discord.Color.blue())
    embed.add_field(name="Nome", value=guild.name, inline=True)
    embed.add_field(name="ID", value=guild.id, inline=True)
    embed.add_field(name="Proprietario", value=guild.owner, inline=True)
    embed.add_field(name="Membri", value=guild.member_count, inline=True)
    embed.add_field(name="Canali", value=len(guild.channels), inline=True)
    embed.add_field(name="Ruoli", value=len(guild.roles), inline=True)
    embed.add_field(name="Data di creazione", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Per vedere la latenza del bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000, 2)
    await interaction.response.send_message(f"Pong! Latency: {latency}ms")

@bot.tree.command(name="say", description="Il messaggio che il bot deve dire")
async def say(interaction: discord.Interaction, *, message: str):
    await interaction.response.send_message(message)

@bot.tree.command(name="guess", description="Indovinello")
async def guess_number(interaction: discord.Interaction):
    number_to_guess = random.randint(1, 100)
    await interaction.response.send_message("Ho scelto un numero da 1 a 100. Prova a indovinarlo!")

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        guess = await bot.wait_for('message', check=check, timeout=30)
        if int(guess.content) == number_to_guess:
            await interaction.channel.send(f"Bravo {interaction.user.mention}, hai indovinato il numero!")
        else:
            await interaction.channel.send(f"Sbagliato! Il numero era {number_to_guess}.")
    except Exception:
        await interaction.channel.send("Tempo scaduto! Riprova.")

@bot.event
async def on_ready():
    print(f'{bot.user} è connesso a Discord!')
    print(f"La latenza del bot è {bot.latency} ms")
    await bot.tree.sync()
    for guild in bot.guilds:
        await bot.tree.sync(guild=guild)
        print(f"Comandi sincronizzati per il server: {guild.name}")

bot.run(TOKEN)