

import discord
from discord.ext import commands
import os

from keep_alive import keep_alive

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ================== IDS (ΒΑΛΕ ΤΑ ΔΙΚΑ ΣΟΥ) ==================

# Roles
SUPPORT_ROLE_ID = 1467220345126654185
MANAGER_ROLE_ID = 1465360458537111582
OWNER_ROLE_ID = 1465345430392017091
CEO_ROLE_ID = 1465362545668788320
PURCHASE_MANAGER_ROLE_ID = 1465398543845032071
AUTOROLE_ID = 1465357638593151331

# Ticket categories
SUPPORT_TICKET_CATEGORY_ID = 1467220343881076767
OWNER_TICKET_CATEGORY_ID = 1467220343881076767
BUY_TICKET_CATEGORY_ID = 1468954499887530147
ORDER_TICKET_CATEGORY_ID = 1468954499887530147
CLAIM_REWARD_CATEGORY_ID = 1468954499887530147

# Temp voice
TEMP_VOICE_CATEGORY_ID = 1465366473030635788          # κατηγορία για temp voice
SUPPORT_VOICE_HUB_ID = 1480255476867535089          # το "κεντρικό" support voice όπου μπαίνουν για να δημιουργηθεί temp

# Logs
TICKET_OPEN_LOG_ID = 1468993859504705643
TICKET_CLOSE_LOG_ID = 1468993859504705643
MOD_LOG_ID = 1468994006632366201
MESSAGE_DELETE_LOG_ID = 1480240608470765690
MESSAGE_EDIT_LOG_ID = 1480240608470765690
JOIN_LOG_ID = 1468994197045641387
LEAVE_LOG_ID = 1468994197045641387
COMMAND_LOG_ID = 1468994006632366201
ROLE_CREATE_LOG_ID = 1468994382828015810
ROLE_DELETE_LOG_ID = 1468994382828015810
ROLE_UPDATE_LOG_ID = 1468994382828015810
VOICE_LOG_ID = 1468994079646814419

# ================== ROLE HELPERS ==================

def is_ceo(member: discord.Member):
    return any(r.id == CEO_ROLE_ID for r in member.roles)

def is_owner_or_ceo(member: discord.Member):
    return any(r.id in [OWNER_ROLE_ID, CEO_ROLE_ID] for r in member.roles)

def is_staff_or_manager(member: discord.Member):
    return any(r.id in [SUPPORT_ROLE_ID, MANAGER_ROLE_ID, OWNER_ROLE_ID, CEO_ROLE_ID] for r in member.roles)

def is_moderator(member: discord.Member):
    return any(r.id in [SUPPORT_ROLE_ID, OWNER_ROLE_ID, CEO_ROLE_ID] for r in member.roles)

# ================== TICKET CLOSE VIEW ==================

class TicketCloseView(discord.ui.View):
    def __init__(self, opener_id: int):
        super().__init__(timeout=None)
        self.opener_id = opener_id

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        channel = interaction.channel
        guild = interaction.guild

        if user.id != self.opener_id and not is_staff_or_manager(user) and not is_owner_or_ceo(user):
            return await interaction.response.send_message("❌ Δεν μπορείς να κλείσεις αυτό το ticket.", ephemeral=True)

        await interaction.response.send_message("🔒 Το ticket θα κλείσει...", ephemeral=False)

        log_ch = guild.get_channel(TICKET_CLOSE_LOG_ID)
        if log_ch:
            embed = discord.Embed(
                title="🔒 Ticket Closed",
                description=f"Κανάλι: {channel.mention}\nΈκλεισε από: {user.mention}",
                color=discord.Color.red()
            )
            await log_ch.send(embed=embed)

        await channel.delete(reason=f"Ticket closed by {user}")

# ================== SUPPORT TICKET PANEL ==================

class SupportTicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", emoji="🛠️", description="Γενικό support"),
            discord.SelectOption(label="Owner Support", emoji="👑", description="Επικοινωνία με Owner/CEO"),
        ]
        super().__init__(placeholder="Επέλεξε κατηγορία ticket...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        if self.values[0] == "Support":
            category = guild.get_channel(SUPPORT_TICKET_CATEGORY_ID)
            allowed_roles = [SUPPORT_ROLE_ID, MANAGER_ROLE_ID]
            ticket_type = "Support"
            prefix = "support"
        else:
            category = guild.get_channel(OWNER_TICKET_CATEGORY_ID)
            allowed_roles = [OWNER_ROLE_ID, CEO_ROLE_ID]
            ticket_type = "Owner Ticket"
            prefix = "owner"

        if not category or not isinstance(category, discord.CategoryChannel):
            return await interaction.response.send_message("❌ Δεν βρέθηκε σωστή κατηγορία για αυτό το ticket.", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }

        for rid in allowed_roles:
            role = guild.get_role(rid)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        name = f"{prefix}-{user.name}".replace(" ", "-").lower()
        channel = await guild.create_text_channel(
            name=name,
            category=category,
            overwrites=overwrites,
            reason=f"{ticket_type} ticket από {user}"
        )

        embed = discord.Embed(
            title=f"🎫 {ticket_type} Ticket",
            description=f"{user.mention} άνοιξε **{ticket_type}** ticket.\nΠεριμένετε απάντηση από την ομάδα.",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed, view=TicketCloseView(opener_id=user.id))

        log_ch = guild.get_channel(TICKET_OPEN_LOG_ID)
        if log_ch:
            log = discord.Embed(
                title="📂 Νέο Ticket",
                description=f"Τύπος: **{ticket_type}**\nΧρήστης: {user.mention}\nΚανάλι: {channel.mention}",
                color=discord.Color.green()
            )
            await log_ch.send(embed=log)

        await interaction.response.send_message(f"✅ Το ticket σου δημιουργήθηκε: {channel.mention}", ephemeral=True)


class SupportTicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SupportTicketSelect())

# ================== BUY TICKET PANEL ==================

class BuyTicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Claim Reward", emoji="🎁", description="Claim your Reward "),
            discord.SelectOption(label="Buy", emoji="🛒", description="Αγορά"),
            discord.SelectOption(label="Order", emoji="📦", description="Παραγγελία"),
        ]
        super().__init__(placeholder="Επέλεξε ένα category...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        if self.values[0] == "Claim Reward":
            category = guild.get_channel(CLAIM_REWARD_CATEGORY_ID)
            allowed_roles = [OWNER_ROLE_ID, CEO_ROLE_ID]
            ticket_type = "Claim Reward"
            prefix = "claim"
        elif self.values[0] == "Buy":
            category = guild.get_channel(BUY_TICKET_CATEGORY_ID)
            allowed_roles = [PURCHASE_MANAGER_ROLE_ID, OWNER_ROLE_ID, CEO_ROLE_ID]
            ticket_type = "Buy"
            prefix = "buy"
        else:
            category = guild.get_channel(ORDER_TICKET_CATEGORY_ID)
            allowed_roles = [OWNER_ROLE_ID, CEO_ROLE_ID]
            ticket_type = "Order"
            prefix = "order"

        if not category or not isinstance(category, discord.CategoryChannel):
            return await interaction.response.send_message("❌ Δεν βρέθηκε σωστή κατηγορία για αυτό το ticket.", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }

        for rid in allowed_roles:
            role = guild.get_role(rid)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        name = f"{prefix}-{user.name}".replace(" ", "-").lower()
        channel = await guild.create_text_channel(
            name=name,
            category=category,
            overwrites=overwrites,
            reason=f"{ticket_type} ticket από {user}"
        )

        embed = discord.Embed(
            title=f"💳 {ticket_type} Ticket",
            description=f"{user.mention} άνοιξε **{ticket_type}** ticket.\nΠεριμένετε απάντηση από την ομάδα.",
            color=discord.Color.gold()
        )
        await channel.send(embed=embed, view=TicketCloseView(opener_id=user.id))

        log_ch = guild.get_channel(TICKET_OPEN_LOG_ID)
        if log_ch:
            log = discord.Embed(
                title="📂 Νέο Buy Ticket",
                description=f"Τύπος: **{ticket_type}**\nΧρήστης: {user.mention}\nΚανάλι: {channel.mention}",
                color=discord.Color.orange()
            )
            await log_ch.send(embed=log)

        await interaction.response.send_message(f"✅ Το ticket σου δημιουργήθηκε: {channel.mention}", ephemeral=True)


class BuyTicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(BuyTicketSelect())

# ================== PANEL COMMANDS ==================

@bot.command()
async def supportpanel(ctx):
    if not is_owner_or_ceo(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα.")
    embed = discord.Embed(
        title="🆘 Support Tickets",
        description="Επέλεξε την κατηγορία που ταιριάζει στο αίτημά σου.",
        color=0x2b2d31
    )
    await ctx.send(embed=embed, view=SupportTicketPanel())

@bot.command()
async def buypanel(ctx):
    if not is_owner_or_ceo(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα.")
    embed = discord.Embed(
        title="💳 Buy Tickets",
        description="Επέλεξε την κατηγορία Ticket που θέλεις.",
        color=0x2b2d31
    )
    await ctx.send(embed=embed, view=BuyTicketPanel())

# ================== SAY / DMALL ==================

@bot.command()
async def say(ctx, *, message: str):
    if not is_ceo(ctx.author):
        return await ctx.reply("❌ Μόνο ο CEO.")
    await ctx.message.delete()
    await ctx.send(message)

class DmApproveView(discord.ui.View):
    def __init__(self, content: str, author_id: int):
        super().__init__(timeout=60)
        self.content = content
        self.author_id = author_id

    @discord.ui.button(label="✅ APPROVE SEND", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id or not is_ceo(interaction.user):
            return await interaction.response.send_message("❌ Δεν μπορείς να εγκρίνεις αυτό το DM.", ephemeral=True)

        await interaction.response.send_message("📨 Στέλνω DM σε όλα τα μέλη...", ephemeral=True)

        sent = 0
        for member in interaction.guild.members:
            if member.bot:
                continue
            try:
                await member.send(self.content)
                sent += 1
            except:
                continue

        await interaction.followup.send(f"✅ Το DM στάλθηκε σε **{sent}** μέλη.", ephemeral=True)
        self.stop()

@bot.command()
async def dmall(ctx, *, message: str):
    if not is_ceo(ctx.author):
        return await ctx.reply("❌ Μόνο ο CEO.")
    embed = discord.Embed(
        title="📨 DM to all — Pending",
        description=f"Μήνυμα:\n```{message}```\n\nΠάτα **APPROVE** για να σταλεί σε όλα τα μέλη.",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed, view=DmApproveView(content=message, author_id=ctx.author.id))

# ================== AUTOROLE ==================

@bot.event
async def on_member_join(member: discord.Member):
    role = member.guild.get_role(AUTOROLE_ID)
    if role:
        try:
            await member.add_roles(role, reason="Autorole")
        except:
            pass

    log_ch = member.guild.get_channel(JOIN_LOG_ID)
    if log_ch:
        await log_ch.send(f"✅ Member joined: {member.mention} ({member.id})")

@bot.event
async def on_member_remove(member: discord.Member):
    log_ch = member.guild.get_channel(LEAVE_LOG_ID)
    if log_ch:
        await log_ch.send(f"❌ Member left: {member.mention} ({member.id})")

# ================== MESSAGE LOGS ==================

@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot or not message.guild:
        return
    log_ch = message.guild.get_channel(MESSAGE_DELETE_LOG_ID)
    if log_ch:
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=f"**User:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Content:**\n{message.content}",
            color=discord.Color.red()
        )
        await log_ch.send(embed=embed)

@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.author.bot or not before.guild:
        return
    if before.content == after.content:
        return
    log_ch = before.guild.get_channel(MESSAGE_EDIT_LOG_ID)
    if log_ch:
        embed = discord.Embed(
            title="✏️ Message Edited",
            description=f"**User:** {before.author.mention}\n**Channel:** {before.channel.mention}",
            color=discord.Color.orange()
        )
        embed.add_field(name="Before", value=before.content or "‎", inline=False)
        embed.add_field(name="After", value=after.content or "‎", inline=False)
        await log_ch.send(embed=embed)

# ================== COMMAND LOGS ==================

@bot.listen("on_command")
async def on_any_command(ctx: commands.Context):
    log_ch = ctx.guild.get_channel(COMMAND_LOG_ID) if ctx.guild else None
    if log_ch:
        await log_ch.send(f"🧾 Command used: `{ctx.message.content}` by {ctx.author.mention} in {ctx.channel.mention}")

# ================== ROLE LOGS ==================

@bot.event
async def on_guild_role_create(role: discord.Role):
    log_ch = role.guild.get_channel(ROLE_CREATE_LOG_ID)
    if log_ch:
        await log_ch.send(f"🆕 Role created: `{role.name}` ({role.id})")

@bot.event
async def on_guild_role_delete(role: discord.Role):
    log_ch = role.guild.get_channel(ROLE_DELETE_LOG_ID)
    if log_ch:
        await log_ch.send(f"🗑️ Role deleted: `{role.name}` ({role.id})")

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    # Role add/remove
    before_roles = set(before.roles)
    after_roles = set(after.roles)

    added = after_roles - before_roles
    removed = before_roles - after_roles

    guild = after.guild
    log_ch = guild.get_channel(ROLE_UPDATE_LOG_ID)
    if not log_ch:
        return

    for role in added:
        if role.is_default():
            continue
        await log_ch.send(f"➕ Role `{role.name}` added to {after.mention}")

    for role in removed:
        if role.is_default():
            continue
        await log_ch.send(f"➖ Role `{role.name}` removed from {after.mention}")

# ================== VOICE LOGS + TEMP VOICE ==================

@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    log_ch = guild.get_channel(VOICE_LOG_ID)

    # Logging
    if before.channel != after.channel:
        if before.channel is None and after.channel is not None:
            if log_ch:
                await log_ch.send(f"🔊 {member.mention} joined voice: `{after.channel.name}`")
        elif before.channel is not None and after.channel is None:
            if log_ch:
                await log_ch.send(f"🔇 {member.mention} left voice: `{before.channel.name}`")
        else:
            if log_ch:
                await log_ch.send(f"🔁 {member.mention} moved: `{before.channel.name}` → `{after.channel.name}`")

    # TEMP VOICE SYSTEM
    temp_category = guild.get_channel(TEMP_VOICE_CATEGORY_ID)

    # 1) Create temp channel when user joins the hub
    if after.channel and after.channel.id == SUPPORT_VOICE_HUB_ID:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False, connect=False),
            member: discord.PermissionOverwrite(view_channel=True, connect=True, speak=True),
        }

        for rid in [SUPPORT_ROLE_ID, MANAGER_ROLE_ID, OWNER_ROLE_ID, CEO_ROLE_ID]:
            role = guild.get_role(rid)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, connect=True, speak=True)

        temp_channel = await guild.create_voice_channel(
            name=f"Support - {member.name}",
            category=temp_category,
            overwrites=overwrites
        )

        await member.move_to(temp_channel)

    # 2) Delete ONLY temp channels (NOT the hub)
    if before.channel:
        # must be inside temp category
        if before.channel.category_id == TEMP_VOICE_CATEGORY_ID:
            # must NOT be the hub
            if before.channel.id != SUPPORT_VOICE_HUB_ID:
                # must be empty
                if len(before.channel.members) == 0:
                    try:
                        await before.channel.delete()
                    except:
                        pass

# ================== MODERATION COMMANDS ==================

@bot.command()
async def clear(ctx, amount: int):
    if not is_moderator(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα.")
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Έγινε clear {amount} μηνύματα.", delete_after=3)

    log_ch = ctx.guild.get_channel(MOD_LOG_ID)
    if log_ch:
        await log_ch.send(f"🧹 Clear {amount} messages by {ctx.author.mention} in {ctx.channel.mention}")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason="No reason"):
    if not is_moderator(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα.")
    await member.kick(reason=reason)
    await ctx.send(f"👢 Έγινε kick ο {member.mention}.")

    log_ch = ctx.guild.get_channel(MOD_LOG_ID)
    if log_ch:
        await log_ch.send(f"👢 Kick: {member.mention} by {ctx.author.mention} | Reason: {reason}")

@bot.command()
async def ban(ctx, member: discord.Member, *, reason="No reason"):
    if not is_moderator(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα.")
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Έγινε ban ο {member.mention}.")

    log_ch = ctx.guild.get_channel(MOD_LOG_ID)
    if log_ch:
        await log_ch.send(f"🔨 Ban: {member.mention} by {ctx.author.mention} | Reason: {reason}")

@bot.command()
async def timeout(ctx, member: discord.Member, minutes: int, *, reason="No reason"):
    if not is_moderator(ctx.author):
        return await ctx.reply("❌ Δεν έχεις δικαίωμα.")
    duration = discord.utils.utcnow() + discord.utils.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"⏳ Timeout {minutes} λεπτά στον {member.mention}.")

    log_ch = ctx.guild.get_channel(MOD_LOG_ID)
    if log_ch:
        await log_ch.send(f"⏳ Timeout: {member.mention} for {minutes} minutes by {ctx.author.mention} | Reason: {reason}")

# ================== READY + PERSISTENT VIEWS ==================

@bot.event
async def on_ready():
    bot.add_view(SupportTicketPanel())
    bot.add_view(BuyTicketPanel())
    print(f"Bot online as {bot.user}")

# ================== RUN (FLASK + TOKEN) ==================

keep_alive()
bot.run(os.getenv("TOKEN"))









