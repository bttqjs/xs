import disnake
from disnake.ext import commands
import logging

# Ustawienia logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Wczytywanie tokena z pliku "t" w tym samym folderze
def load_token():
    try:
        with open("t", "r") as file:
            return file.read().strip()
    except Exception as e:
        logger.error(f"Error loading token: {e}")
        raise

# Konfiguracja bota
bot = commands.Bot(command_prefix="!", intents=disnake.Intents.all(), test_guilds=[1303682942161260584])  # Dodaj testowe guild ID

# ID kanału i serwera
GUILD_ID = 1303682942161260584
CHANNEL_ID = 1303682942924750940
ROLE_ID = 1303692928593428533

# Tworzenie przycisku w formie Button
async def verification_button(channel: disnake.TextChannel):
    embed = disnake.Embed(
        title="Welcome!",
        description="Click the button below to verify your account.",
        color=0x00FF00
    )
    await channel.send(embed=embed, components=[ 
        disnake.ui.Button(style=disnake.ButtonStyle.primary, label="Verify Account", custom_id="verify_account")
    ])
    logger.info("Verification button sent to channel.")

@bot.event
async def on_ready():
    logger.info(f'Bot {bot.user} is ready')
    
    # Rejestracja komend Slash (przy pierwszym uruchomieniu)
    await bot.tree.sync()
    
    try:
        channel = await bot.fetch_channel(CHANNEL_ID)
        await verification_button(channel)
    except Exception as e:
        logger.error(f"Error in on_ready: {e}")

# Używamy on_interaction do obsługi przycisku
@bot.event
async def on_interaction(interaction: disnake.Interaction):
    try:
        logger.info(f"Interaction received: {interaction.type}")

        # Sprawdzamy, czy interakcja jest typu component (kliknięcie przycisku)
        if interaction.type == disnake.InteractionType.component:
            logger.info(f"Button clicked: {interaction.data['custom_id']}")

            # Sprawdzamy, czy kliknięto przycisk "verify_account"
            if interaction.data["custom_id"] == "verify_account":
                logger.info("Sending modal for account verification.")
                modal = disnake.ui.Modal(title="Account Verification", components=[
                    disnake.ui.TextInput(label="Oldschool RuneScape Nickname", custom_id="nickname", required=True),
                    disnake.ui.TextInput(label="Solve this math: 2x2+2", custom_id="math_answer", required=True)
                ])
                await interaction.response.send_modal(modal)  # Wyświetlenie modala
        else:
            logger.warning(f"Unknown interaction type: {interaction.type}")
    except Exception as e:
        logger.error(f"Error in on_interaction: {e}")

# Obsługa formularza z modalem
@bot.event
async def on_modal_submit(interaction: disnake.ModalInteraction):
    try:
        # Logowanie informacji o modalnym formularzu
        logger.info(f"Modal submitted by {interaction.user.id}. Processing...")
        
        # Pobieramy dane z formularza
        nickname = interaction.text_values["nickname"]
        math_answer = interaction.text_values["math_answer"]
        
        # Uzyskujemy użytkownika i serwer
        user = interaction.user
        guild = interaction.guild
        bot_member = guild.get_member(bot.user.id)
        
        # Logowanie informacji o sprawdzaniu uprawnień bota
        logger.info(f"Bot's permissions: Manage Roles - {bot_member.guild_permissions.manage_roles}, Change Nickname - {bot_member.guild_permissions.change_nickname}")
        
        # Sprawdzamy, czy bot ma wymagane uprawnienia
        if not bot_member.guild_permissions.manage_roles or not bot_member.guild_permissions.change_nickname:
            await interaction.response.send_message(
                "Bot does not have the required permissions to manage roles or change nicknames.", 
                ephemeral=True
            )
            logger.error("Bot does not have the required permissions.")
            return

        # Sprawdzamy odpowiedź na pytanie matematyczne
        if math_answer == "6":
            # Pobieramy rolę na podstawie ID
            role = disnake.utils.get(guild.roles, id=ROLE_ID)
            
            if role:
                # Zmiana nicku użytkownika
                await user.edit(nick=nickname)
                # Dodanie roli do użytkownika
                await user.add_roles(role)
                await interaction.response.send_message("Verification successful!", ephemeral=True)
                logger.info(f"Verification successful for {user.id}")
            else:
                await interaction.response.send_message("Role not found.", ephemeral=True)
                logger.warning(f"Role with ID {ROLE_ID} not found.")
        else:
            await interaction.response.send_message("Incorrect answer. Please try again.", ephemeral=True)
            logger.warning(f"Incorrect answer submitted by {user.id}: {math_answer}")
    
    except Exception as e:
        # Logowanie wyjątków
        logger.error(f"Error in on_modal_submit: {e}")
        await interaction.response.send_message("An error occurred during verification. Please try again later.", ephemeral=True)

@bot.tree.command(name="purge", description="Usuń wszystkie wiadomości na tym kanale")
async def purge(interaction: disnake.Interaction):
    # Sprawdzamy, czy użytkownik wykonujący komendę ma odpowiednie ID
    if interaction.user.id != 633600812970541056:  # Twoje ID
        await interaction.response.send_message("Nie masz uprawnień do używania tej komendy.", ephemeral=True)
        return

    # Sprawdzamy, czy bot ma odpowiednie uprawnienia do usuwania wiadomości
    if not interaction.guild.me.guild_permissions.manage_messages:
        await interaction.response.send_message("Bot nie ma uprawnień do zarządzania wiadomościami.", ephemeral=True)
        return

    # Usuwamy wiadomości na kanale
    try:
        deleted = await interaction.channel.purge(limit=100)  # Usuwamy ostatnie 100 wiadomości (możesz zmienić limit)
        await interaction.response.send_message(f"Usunięto {len(deleted)} wiadomości.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Wystąpił błąd podczas usuwania wiadomości: {e}", ephemeral=True)
        logger.error(f"Error in purge command: {e}")

bot.run(load_token())  # Uruchomienie bota
