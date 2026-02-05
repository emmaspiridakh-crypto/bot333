import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ==========================
# ROLE IDs
# ==========================

OWNER_ROLE_ID = 1465345430392017091
CEO_ROLE_ID = 1465362545668788320
MANAGER_ROLE_ID = 1465360458537111582
STAFF_ROLE_ID = 1467220345126654185

# ==========================
# LOG CHANNEL IDs (ΒΑΛΕ ΤΑ ΔΙΚΑ ΣΟΥ)
# ==========================

TICKET_LOG_CHANNEL_ID = 1468993859504705643
APPLICATION_LOG_CHANNEL_ID = 1468994006632366201
VOICE_LOG_CHANNEL_ID = 1468994079646814419
MEMBER_LOG_CHANNEL_ID = 1468994197045641387
CHANNEL_LOG_CHANNEL_ID = 1468994309708579108
ROLE_LOG_CHANNEL_ID = 1468994382828015810

SUPPORT_TICKET_CATEGORY_ID = 1467220343881076767
BUY_TICKET_CATEGORY_ID = 1468954499887530147
APPLICATION_CATEGORY_ID = 1468954618414497823
SUPPORT_CALL_VC_ID = 1465366816959234109
TEMP_SUPPORT_CATEGORY_ID = 1465366473030635788

# ==========================
# PERMISSION FUNCTIONS
# ==========================


def is_staff_or_higher(user):
    staff_roles = {STAFF_ROLE_ID, MANAGER_ROLE_ID, CEO_ROLE_ID, OWNER_ROLE_ID}
    return any(role.id in staff_roles for role in user.roles)


def is_owner_or_ceo(user):
    high_roles = {CEO_ROLE_ID, OWNER_ROLE_ID}
    return any(role.id in high_roles for role in user.roles)


# ==========================
# LOG SYSTEM
# ==========================

from discord import Embed


# --------------------------
# TICKET LOGS
# --------------------------
async def log_ticket_open(channel, user, staff=None):
    log = channel.guild.get_channel(TICKET_LOG_CHANNEL_ID)
    if not log:
        return

    embed = Embed(title="🎫 Ticket Opened", color=0x00ff00)
    embed.add_field(name="User", value=f"{user} (`{user.id}`)", inline=False)
    if staff:
        embed.add_field(name="Opened by Staff",
                        value=f"{staff} (`{staff.id}`)",
                        inline=False)
    embed.add_field(name="Channel", value=channel.mention, inline=False)
    embed.timestamp = discord.utils.utcnow()

    await log.send(embed=embed)


async def log_ticket_close(channel, staff):
    log = channel.guild.get_channel(TICKET_LOG_CHANNEL_ID)
    if not log:
        return

    embed = Embed(title="🧨 Ticket Closed", color=0xff0000)
    embed.add_field(name="Closed by",
                    value=f"{staff} (`{staff.id}`)",
                    inline=False)
    embed.add_field(name="Channel", value=channel.name, inline=False)
    embed.timestamp = discord.utils.utcnow()

    await log.send(embed=embed)


# --------------------------
# APPLICATION LOGS
# --------------------------


async def log_application_open(channel, user):
    log = channel.guild.get_channel(APPLICATION_LOG_CHANNEL_ID)
    if not log:
        return

    embed = Embed(title="📨 Application Opened", color=0x3498db)
    embed.add_field(name="Applicant",
                    value=f"{user} (`{user.id}`)",
                    inline=False)
    embed.add_field(name="Channel", value=channel.mention, inline=False)
    embed.timestamp = discord.utils.utcnow()

    await log.send(embed=embed)


async def log_application_status(channel,
                                 applicant,
                                 staff,
                                 status,
                                 reason=None):
    log = channel.guild.get_channel(APPLICATION_LOG_CHANNEL_ID)
    if not log:
        return

    color = 0x2ecc71 if status == "accepted" else 0xe74c3c

    embed = Embed(title=f"📌 Application {status.upper()}", color=color)
    embed.add_field(name="Applicant",
                    value=f"{applicant} (`{applicant.id}`)",
                    inline=False)
    embed.add_field(name="Staff",
                    value=f"{staff} (`{staff.id}`)",
                    inline=False)
    embed.add_field(name="Channel", value=channel.mention, inline=False)

    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)

    embed.timestamp = discord.utils.utcnow()

    await log.send(embed=embed)


async def log_application_close(channel, staff):
    log = channel.guild.get_channel(APPLICATION_LOG_CHANNEL_ID)
    if not log:
        return

    embed = Embed(title="📪 Application Closed", color=0x95a5a6)
    embed.add_field(name="Closed by",
                    value=f"{staff} (`{staff.id}`)",
                    inline=False)
    embed.add_field(name="Channel", value=channel.name, inline=False)
    embed.timestamp = discord.utils.utcnow()

    await log.send(embed=embed)


# --------------------------
# VOICE LOGS
# --------------------------


@bot.event
async def on_voice_state_update(member, before, after):
    log = member.guild.get_channel(VOICE_LOG_CHANNEL_ID)
    if not log:
        return

    # Join
    if before.channel is None and after.channel is not None:
        embed = Embed(
            title="🔊 Voice Join",
            description=f"{member.mention} μπήκε στο {after.channel.mention}",
            color=0x2ecc71)
        embed.timestamp = discord.utils.utcnow()
        await log.send(embed=embed)

    # Leave
    elif before.channel is not None and after.channel is None:
        embed = Embed(
            title="🔇 Voice Leave",
            description=f"{member.mention} βγήκε από {before.channel.mention}",
            color=0xe74c3c)
        embed.timestamp = discord.utils.utcnow()
        await log.send(embed=embed)

    # Move
    elif before.channel and after.channel and before.channel.id != after.channel.id:
        embed = Embed(
            title="🔁 Voice Move",
            description=
            f"{member.mention} μετακινήθηκε από {before.channel.mention} → {after.channel.mention}",
            color=0xf1c40f)
        embed.timestamp = discord.utils.utcnow()
        await log.send(embed=embed)


# --------------------------
# MEMBER LOGS
# --------------------------


@bot.event
async def on_member_join(member):
    log = member.guild.get_channel(MEMBER_LOG_CHANNEL_ID)
    if not log:
        return

    embed = Embed(title="✅ Member Joined",
                  description=f"{member} (`{member.id}`) μπήκε στον server.",
                  color=0x2ecc71)
    embed.timestamp = discord.utils.utcnow()
    await log.send(embed=embed)


@bot.event
async def on_member_remove(member):
    log = member.guild.get_channel(MEMBER_LOG_CHANNEL_ID)
    if not log:
        return

    embed = Embed(
        title="❌ Member Left",
        description=f"{member} (`{member.id}`) έφυγε από τον server.",
        color=0xe74c3c)
    embed.timestamp = discord.utils.utcnow()
    await log.send(embed=embed)


# --------------------------
# CHANNEL LOGS
# --------------------------


@bot.event
async def on_guild_channel_create(channel):
    log = channel.guild.get_channel(CHANNEL_LOG_CHANNEL_ID)
    if not log:
        return

    embed = Embed(title="📁 Channel Created",
                  description=f"{channel.mention} δημιουργήθηκε.",
                  color=0x2ecc71)
    embed.timestamp = discord.utils.utcnow()
    await log.send(embed=embed)


@bot.event
async def on_guild_channel_delete(channel):
    log = channel.guild.get_channel(CHANNEL_LOG_CHANNEL_ID)
    if not log:
        return

    embed = Embed(title="🗑️ Channel Deleted",
                  description=f"{channel.name} διαγράφηκε.",
                  color=0xe74c3c)
    embed.timestamp = discord.utils.utcnow()
    await log.send(embed=embed)


# --------------------------
# ROLE LOGS
# --------------------------


@bot.event
async def on_member_update(before, after):
    log = after.guild.get_channel(ROLE_LOG_CHANNEL_ID)
    if not log:
        return

    before_roles = set(before.roles)
    after_roles = set(after.roles)

    added = after_roles - before_roles
    removed = before_roles - after_roles

    for role in added:
        embed = Embed(title="➕ Role Added",
                      description=f"{after} πήρε τον ρόλο {role.mention}",
                      color=0x2ecc71)
        embed.timestamp = discord.utils.utcnow()
        await log.send(embed=embed)

    for role in removed:
        embed = Embed(title="➖ Role Removed",
                      description=f"{after} έχασε τον ρόλο {role.mention}",
                      color=0xe74c3c)
        embed.timestamp = discord.utils.utcnow()
        await log.send(embed=embed)


# ==========================
# APPLICATION PANELS
# ==========================


class StaffApplicationPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Apply for Staff",
                       style=discord.ButtonStyle.primary)
    async def apply_staff(self, interaction, button):
        modal = StaffApplicationModal()
        await interaction.response.send_modal(modal)


class ManagerApplicationPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Apply for Manager",
                       style=discord.ButtonStyle.danger)
    async def apply_manager(self, interaction, button):
        modal = ManagerApplicationModal()
        await interaction.response.send_modal(modal)


# ==========================
# STAFF APPLICATION MODAL
# ==========================


class StaffApplicationModal(discord.ui.Modal, title="Staff Application"):

    q1 = discord.ui.TextInput(label="Πόσο χρονών είσαι;",
                              style=discord.TextStyle.short)
    q2 = discord.ui.TextInput(
        label="Πόσες ώρες θα μπορείς να είσαι on duty την μέρα;",
        style=discord.TextStyle.short)
    q3 = discord.ui.TextInput(label="Τι είναι η ιεραρχία για σένα;",
                              style=discord.TextStyle.paragraph)
    q4 = discord.ui.TextInput(label="Έχεις εμπειρία πάνω στο staff κομμάτι;",
                              style=discord.TextStyle.paragraph)
    q5 = discord.ui.TextInput(label="Πες 3 βασικά rules του server",
                              style=discord.TextStyle.paragraph)
    q6 = discord.ui.TextInput(
        label="Τι θα κάνεις αν δεν μπορείς να βοηθήσεις κάποιον;",
        style=discord.TextStyle.paragraph)
    q7 = discord.ui.TextInput(
        label="Πως θα αντιδράσεις σε αντιεπαγγελματική συμπεριφορά staff;",
        style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction):
        guild = interaction.guild
        category = guild.get_channel(APPLICATION_CATEGORY_ID)

        channel = await guild.create_text_channel(
            name=f"staff-app-{interaction.user.name}",
            category=category,
            overwrites={
                guild.default_role:
                discord.PermissionOverwrite(view_channel=False),
                guild.get_role(OWNER_ROLE_ID):
                discord.PermissionOverwrite(view_channel=True,
                                            send_messages=True),
                guild.get_role(CEO_ROLE_ID):
                discord.PermissionOverwrite(view_channel=True,
                                            send_messages=True),
            })

        # LOG: Application Open
        await log_application_open(channel, interaction.user)

        embed = discord.Embed(title="Νέα Staff Αίτηση",
                              color=discord.Color.blue())
        embed.add_field(name="User",
                        value=f"{interaction.user} ({interaction.user.id})",
                        inline=False)
        embed.add_field(name="Πόσο χρονών είσαι;",
                        value=self.q1.value,
                        inline=False)
        embed.add_field(name="Ώρες on duty", value=self.q2.value, inline=False)
        embed.add_field(name="Τι είναι η ιεραρχία;",
                        value=self.q3.value,
                        inline=False)
        embed.add_field(name="Εμπειρία staff",
                        value=self.q4.value,
                        inline=False)
        embed.add_field(name="3 βασικά rules",
                        value=self.q5.value,
                        inline=False)
        embed.add_field(name="Αν δεν μπορείς να βοηθήσεις",
                        value=self.q6.value,
                        inline=False)
        embed.add_field(name="Αντιεπαγγελματική συμπεριφορά staff",
                        value=self.q7.value,
                        inline=False)

        await channel.send(embed=embed,
                           view=ApplicationDecisionView(interaction.user.id))
        await interaction.response.send_message("Η αίτησή σου στάλθηκε!",
                                                ephemeral=True)


# ==========================
# MANAGER APPLICATION MODAL
# ==========================


class ManagerApplicationModal(discord.ui.Modal, title="Manager Application"):

    q1 = discord.ui.TextInput(label="Πόσο χρονών είσαι;",
                              style=discord.TextStyle.short)
    q2 = discord.ui.TextInput(
        label="Πόσες ώρες θα μπορείς να είσαι on duty την ημέρα;",
        style=discord.TextStyle.short)
    q3 = discord.ui.TextInput(label="Ανέφερε 3 βασικά rules του server",
                              style=discord.TextStyle.paragraph)
    q4 = discord.ui.TextInput(label="Τι είναι η ιεραρχία για σένα;",
                              style=discord.TextStyle.paragraph)
    q5 = discord.ui.TextInput(
        label="Έχεις εμπειρία πάνω στο κομμάτι management;",
        style=discord.TextStyle.paragraph)
    q6 = discord.ui.TextInput(
        label="Πως θα αντιμετώπιζες μια δύσκολη σύγκρουση στο team;",
        style=discord.TextStyle.paragraph)
    q7 = discord.ui.TextInput(
        label="Τι θα έκανες αν κάποιος δεν άκουγε τις εντολές σου;",
        style=discord.TextStyle.paragraph)
    q8 = discord.ui.TextInput(
        label="Τι θα έκανες αν δεν σου αρέσει εντολή ανώτερου;",
        style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction):
        guild = interaction.guild
        category = guild.get_channel(APPLICATION_CATEGORY_ID)

        channel = await guild.create_text_channel(
            name=f"manager-app-{interaction.user.name}",
            category=category,
            overwrites={
                guild.default_role:
                discord.PermissionOverwrite(view_channel=False),
                guild.get_role(OWNER_ROLE_ID):
                discord.PermissionOverwrite(view_channel=True,
                                            send_messages=True),
                guild.get_role(CEO_ROLE_ID):
                discord.PermissionOverwrite(view_channel=True,
                                            send_messages=True),
            })

        # LOG: Application Open
        await log_application_open(channel, interaction.user)

        embed = discord.Embed(title="Νέα Manager Αίτηση",
                              color=discord.Color.green())
        embed.add_field(name="User",
                        value=f"{interaction.user} ({interaction.user.id})",
                        inline=False)
        embed.add_field(name="Πόσο χρονών είσαι;",
                        value=self.q1.value,
                        inline=False)
        embed.add_field(name="Ώρες on duty", value=self.q2.value, inline=False)
        embed.add_field(name="3 βασικά rules",
                        value=self.q3.value,
                        inline=False)
        embed.add_field(name="Τι είναι η ιεραρχία;",
                        value=self.q4.value,
                        inline=False)
        embed.add_field(name="Εμπειρία management",
                        value=self.q5.value,
                        inline=False)
        embed.add_field(name="Αντιμετώπιση σύγκρουσης",
                        value=self.q6.value,
                        inline=False)
        embed.add_field(name="Αν δεν ακούει εντολές",
                        value=self.q7.value,
                        inline=False)
        embed.add_field(name="Αν δεν σου αρέσει εντολή ανώτερου",
                        value=self.q8.value,
                        inline=False)

        await channel.send(embed=embed,
                           view=ApplicationDecisionView(interaction.user.id))
        await interaction.response.send_message("Η αίτησή σου στάλθηκε!",
                                                ephemeral=True)


# ==========================
# ACCEPT / DENY BUTTONS
# ==========================


class ApplicationDecisionView(discord.ui.View):

    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="Accept with reason",
                       style=discord.ButtonStyle.success)
    async def accept(self, interaction, button):
        if not is_owner_or_ceo(interaction.user):
            return await interaction.response.send_message(
                "Δεν έχεις δικαίωμα.", ephemeral=True)

        modal = AcceptModal(self.user_id)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Denied with reason",
                       style=discord.ButtonStyle.danger)
    async def deny(self, interaction, button):
        if not is_owner_or_ceo(interaction.user):
            return await interaction.response.send_message(
                "Δεν έχεις δικαίωμα.", ephemeral=True)

        modal = DenyModal(self.user_id)
        await interaction.response.send_modal(modal)


# ==========================
# ACCEPT MODAL
# ==========================


class AcceptModal(discord.ui.Modal, title="Accept Application"):
    reason = discord.ui.TextInput(label="Reason",
                                  style=discord.TextStyle.paragraph)

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

    async def on_submit(self, interaction):
        guild = interaction.guild
        applicant = guild.get_member(self.user_id)

        # LOG: Accepted
        await log_application_status(interaction.channel, applicant,
                                     interaction.user, "accepted",
                                     self.reason.value)

        await interaction.response.send_message("Η αίτηση έγινε **δεκτή**.",
                                                ephemeral=True)


# ==========================
# DENY MODAL
# ==========================


class DenyModal(discord.ui.Modal, title="Deny Application"):
    reason = discord.ui.TextInput(label="Reason",
                                  style=discord.TextStyle.paragraph)

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

    async def on_submit(self, interaction):
        guild = interaction.guild
        applicant = guild.get_member(self.user_id)

        # LOG: Denied
        await log_application_status(interaction.channel, applicant,
                                     interaction.user, "denied",
                                     self.reason.value)

        await interaction.response.send_message("Η αίτηση **απορρίφθηκε**.",
                                                ephemeral=True)


# ==========================
# SUPPORT TICKET PANEL
# ==========================


class SupportTicketPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Support📞", style=discord.ButtonStyle.green)
    async def general_support(self, interaction, button):
        await create_ticket(interaction,
                            ticket_type="support",
                            category_id=SUPPORT_TICKET_CATEGORY_ID,
                            allowed_roles=[
                                STAFF_ROLE_ID, MANAGER_ROLE_ID, CEO_ROLE_ID,
                                OWNER_ROLE_ID
                            ])

    @discord.ui.button(label="Owner👑", style=discord.ButtonStyle.green)
    async def report(self, interaction, button):
        await create_ticket(interaction,
                            ticket_type="owner",
                            category_id=SUPPORT_TICKET_CATEGORY_ID,
                            allowed_roles=[CEO_ROLE_ID, OWNER_ROLE_ID])


# ==========================
# BUY TICKET PANEL
# ==========================


class BuyTicketPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Buy💸", style=discord.ButtonStyle.green)
    async def buy_product(self, interaction, button):
        await create_ticket(interaction,
                            ticket_type="buy",
                            category_id=BUY_TICKET_CATEGORY_ID,
                            allowed_roles=[
                                STAFF_ROLE_ID, MANAGER_ROLE_ID, CEO_ROLE_ID,
                                OWNER_ROLE_ID
                            ])

    @discord.ui.button(label="Order📦", style=discord.ButtonStyle.green)
    async def order(self, interaction, button):
        await create_ticket(
            interaction,
            ticket_type="Order",
            category_id=BUY_TICKET_CATEGORY_ID,
            allowed_roles=[MANAGER_ROLE_ID, CEO_ROLE_ID, OWNER_ROLE_ID])

    @discord.ui.button(label="Claim Reward🏆", style=discord.ButtonStyle.green)
    async def claim_reward(self, interaction, button):
        await create_ticket(interaction,
                            ticket_type="buy",
                            category_id=BUY_TICKET_CATEGORY_ID,
                            allowed_roles=[
                                STAFF_ROLE_ID, MANAGER_ROLE_ID, CEO_ROLE_ID,
                                OWNER_ROLE_ID
                            ])


# ==========================
# TICKET CLOSE BUTTON
# ==========================


class TicketCloseView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction, button):
        if not is_staff_or_higher(interaction.user):
            return await interaction.response.send_message(
                "Δεν έχεις δικαίωμα.", ephemeral=True)

        await interaction.response.send_message(
            "Το ticket θα κλείσει σε 5 δευτερόλεπτα…", ephemeral=True)
        await asyncio.sleep(5)

        # LOG: Ticket Close
        await log_ticket_close(interaction.channel, interaction.user)

        try:
            await interaction.channel.delete(reason="Ticket closed")
        except:
            pass


# ==========================
# TICKET CREATION FUNCTION
# ==========================


async def create_ticket(interaction, ticket_type, category_id, allowed_roles):
    guild = interaction.guild
    category = guild.get_channel(category_id)

    overwrites = {
        guild.default_role:
        discord.PermissionOverwrite(view_channel=False),
        interaction.user:
        discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    # Add staff roles
    for role_id in allowed_roles:
        role = guild.get_role(role_id)
        if role:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True,
                                                           send_messages=True)

    # Create channel
    channel = await guild.create_text_channel(
        name=f"{ticket_type}-{interaction.user.name}",
        category=category,
        overwrites=overwrites)

    # LOG: Ticket Open
    await log_ticket_open(channel, interaction.user, staff=interaction.user)

    embed = discord.Embed(
        title=f"{ticket_type.capitalize()} Ticket",
        description="Ένα μέλος του staff θα σε εξυπηρετήσει σύντομα.",
        color=discord.Color.dark_green())

    await channel.send(embed=embed, view=TicketCloseView())
    await interaction.response.send_message(
        f"Το ticket σου δημιουργήθηκε: {channel.mention}", ephemeral=True)


# ==========================
# SEND PANELS COMMAND
# ==========================


@bot.command()
async def send(ctx, panel_type=None, panel_name=None):
    if panel_type is None or panel_name is None:
        return await ctx.reply("Χρησιμοποίησε:\n"
                               "`!send support panel`\n"
                               "`!send buy panel`\n"
                               "`!send staff panel`\n"
                               "`!send managers panel`")

    panel_type = panel_type.lower()
    panel_name = panel_name.lower()

    # SUPPORT PANEL
    if panel_type == "support" and panel_name == "panel":
        if not is_staff_or_higher(ctx.author):
            return await ctx.reply("Δεν έχεις δικαίωμα.")
        embed = discord.Embed(
            title="Support Panel",
            description=
            "Αν χρειάζεσαι βοήθεια ή έχεις κάποια ερώτηση πάτα για να ανοίξεις ένα ticket🎫!",
            color=discord.Color.gold())
        return await ctx.send(embed=embed, view=SupportTicketPanel())

    # BUY PANEL
    if panel_type == "buy" and panel_name == "panel":
        if not is_staff_or_higher(ctx.author):
            return await ctx.reply("Δεν έχεις δικαίωμα.")
        embed = discord.Embed(
            title="Buy Panel",
            description=
            "Αν θες να αγοράσεις κάτι, να κάνεις μια παραγγελία ή να συλλέξεις το reward σου, πάτα για να ανοίξεις το αντίστοιχο ticket",
            color=discord.Color.dark_green())
        return await ctx.send(embed=embed, view=BuyTicketPanel())

    # STAFF APPLICATION PANEL
    if panel_type == "staff" and panel_name == "panel":
        if not is_owner_or_ceo(ctx.author):
            return await ctx.reply("Μόνο Owner/CEO.")
        embed = discord.Embed(
            title="Staff Application Panel",
            description="Πατήστε το κουμπί για να κάνετε αίτηση Staff.",
            color=discord.Color.dark_grey())
        return await ctx.send(embed=embed, view=StaffApplicationPanel())

    # MANAGERS APPLICATION PANEL
    if panel_type == "managers" and panel_name == "panel":
        if not is_owner_or_ceo(ctx.author):
            return await ctx.reply("Μόνο Owner/CEO.")
        embed = discord.Embed(
            title="Managers Application Panel",
            description="Πατήστε το κουμπί για να κάνετε αίτηση Manager.",
            color=discord.Color.dark_gray())
        return await ctx.send(embed=embed, view=ManagerApplicationPanel())

    await ctx.reply("Λάθος χρήση εντολής.")


# ==========================
# SAY COMMAND
# ==========================


@bot.command()
async def say(ctx, *, text=None):
    if not is_staff_or_higher(ctx.author):
        return await ctx.reply("Δεν έχεις δικαίωμα.")
    if not text:
        return await ctx.reply("Γράψε τι να πω.")
    try:
        await ctx.message.delete()
    except:
        pass
    await ctx.send(text)


# ==========================
# DMALL COMMAND
# ==========================


@bot.command()
async def dmall(ctx, *, text=None):
    if not is_owner_or_ceo(ctx.author):
        return await ctx.reply("Μόνο Owner/CEO.")
    if not text:
        return await ctx.reply("Γράψε μήνυμα.")
    await ctx.reply("Ξεκινάω να στέλνω DM…")

    async for member in ctx.guild.fetch_members(limit=None):
        if member.bot:
            continue
        try:
            await member.send(text)
        except:
            pass
        await ctx.send(text)


# ==========================
# MODERATION COMMANDS
# ==========================


@bot.command()
async def kick(ctx, member: discord.Member = None, *, reason=None):
    if not is_staff_or_higher(ctx.author):
        return await ctx.reply("Δεν έχεις δικαίωμα.")
    if member is None:
        return await ctx.reply("Κάνε mention τον χρήστη.")
    if reason is None:
        return await ctx.reply("Γράψε reason.")
    try:
        await member.kick(reason=reason)
        await ctx.reply(f"Kick: {member.mention} | Reason: {reason}")
    except:
        await ctx.reply("Δεν μπόρεσα να κάνω kick.")


@bot.command()
async def ban(ctx, member: discord.Member = None, *, reason=None):
    if not is_staff_or_higher(ctx.author):
        return await ctx.reply("Δεν έχεις δικαίωμα.")
    if member is None:
        return await ctx.reply("Κάνε mention τον χρήστη.")
    if reason is None:
        return await ctx.reply("Γράψε reason.")
    try:
        await member.ban(reason=reason)
        await ctx.reply(f"Ban: {member.mention} | Reason: {reason}")
    except:
        await ctx.reply("Δεν μπόρεσα να κάνω ban.")


@bot.command()
async def unban(ctx, user_id: int = None, *, reason=None):
    if not is_staff_or_higher(ctx.author):
        return await ctx.reply("Δεν έχεις δικαίωμα.")
    if user_id is None:
        return await ctx.reply("Γράψε user ID.")
    if reason is None:
        return await ctx.reply("Γράψε reason.")
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)
        await ctx.reply(f"Unban: {user} | Reason: {reason}")
    except:
        await ctx.reply("Δεν μπόρεσα να κάνω unban.")


@bot.command()
async def timeout(ctx,
                  member: discord.Member = None,
                  minutes: int = None,
                  *,
                  reason=None):
    if not is_staff_or_higher(ctx.author):
        return await ctx.reply("Δεν έχεις δικαίωμα.")
    if member is None:
        return await ctx.reply("Κάνε mention.")
    if minutes is None:
        return await ctx.reply("Γράψε λεπτά.")
    if reason is None:
        return await ctx.reply("Γράψε reason.")

    try:
        until = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
        await member.edit(timeout=until, reason=reason)
        await ctx.reply(
            f"Timeout: {member.mention} για {minutes} λεπτά | Reason: {reason}"
        )
    except:
        await ctx.reply("Δεν μπόρεσα να κάνω timeout.")


# ==========================
# BOT PANEL
# ==========================


@bot.command()
async def botpanel(ctx):
    embed = discord.Embed(title="Bot Panel", color=discord.Color.purple())
    embed.add_field(name="General", value="!say, !dmall", inline=False)
    embed.add_field(name="Tickets",
                    value="!send support panel, !send buy panel",
                    inline=False)
    embed.add_field(name="Applications",
                    value="!send staff panel, !send managers panel",
                    inline=False)
    embed.add_field(name="Moderation",
                    value="!kick, !ban, !unban, !timeout",
                    inline=False)
    await ctx.send(embed=embed)


# ==========================
# TEMPORARY SUPPORT CALL
# ==========================


@bot.event
async def on_voice_state_update(member, before, after):

    # --- TEMP SUPPORT CALL CREATION ---
    try:
        # Αν ο χρήστης ΜΠΗΚΕ σε συγκεκριμένο voice channel
        if after.channel and after.channel.id == SUPPORT_CALL_VC_ID:

            guild = member.guild
            category = guild.get_channel(TEMP_SUPPORT_CATEGORY_ID)

            overwrites = {
                guild.default_role:
                discord.PermissionOverwrite(view_channel=False, connect=False),
                member:
                discord.PermissionOverwrite(view_channel=True, connect=True),
                guild.get_role(STAFF_ROLE_ID):
                discord.PermissionOverwrite(view_channel=True, connect=True),
                guild.get_role(MANAGER_ROLE_ID):
                discord.PermissionOverwrite(view_channel=True, connect=True),
                guild.get_role(CEO_ROLE_ID):
                discord.PermissionOverwrite(view_channel=True, connect=True),
                guild.get_role(OWNER_ROLE_ID):
                discord.PermissionOverwrite(view_channel=True, connect=True),
            }

            # Δημιουργία προσωρινού voice channel
            temp_channel = await guild.create_voice_channel(
                name=f"support-{member.name}",
                category=category,
                overwrites=overwrites,
                reason="Temporary support call")

            # Μετακίνηση χρήστη στο νέο κανάλι
            await member.move_to(temp_channel)

            # Διαγραφή όταν αδειάσει
            async def delete_when_empty():
                await asyncio.sleep(3)
                while True:
                    ch = guild.get_channel(temp_channel.id)
                    if not ch or len(ch.members) == 0:
                        try:
                            await ch.delete(reason="Temp support call empty")
                        except:
                            pass
                        break
                    await asyncio.sleep(10)

            bot.loop.create_task(delete_when_empty())

    except Exception as e:
        print("Temp call error:", e)

# ==========================
# RUN BOT
# ==========================
bot.run("MTQ2ODU3OTQzNDA5NjM2NTU2OA.Grgy05.1K2ZgIAMQLK0N10Wj6S9eso00UnDCaW6jrKDxo")