# --- この下からすべてコピー ---
import discord
from discord.ext import commands
from discord.ui import View, Button, button
import os # 1. osモジュールをインポート

# -------------------- 設定 --------------------
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ご自身の環境に合わせてIDを設定してください
GUILD_ID = 1369044767702253608    # 対象のサーバー（ギルド）ID
HOST_ROLE_ID = 1409154676045381713  # 親となる「ロール」のID

# --- チャンネルとロールのID ---
VC1_ID = 1369044768440582297 # VC-1: 通知が行われるチャンネル
VC2_ID = 1369045799803027586    # VC-2: 通知が行われないチャンネル

VIEWER_ROLE_ID = 1409157639367032923      # 視聴者ロール
VERIFIED_ROLE_ID = 1409164397242355724    # 認証ボタンで付与するロール
NOTIFICATION_CHANNEL_ID = 1427703021789380789 # 通知メッセージを送信するテキストチャンネルのID
# ----------------------------------------------


# --- 認証ボタンのクラス ---
class RoleButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)
    @button(label="規約に同意してチャンネルを閲覧する", style=discord.ButtonStyle.success, custom_id="persistent_view:verify_role")
    async def verify_button(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(VERIFIED_ROLE_ID)
        if not role: await interaction.response.send_message("エラー: ロールが見つかりません。", ephemeral=True); return
        if role in interaction.user.roles: await interaction.response.send_message("すでに認証済みです。", ephemeral=True); return
        try:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("認証が完了しました！チャンネルをお楽しみください。", ephemeral=True)
            print(f"{interaction.user.display_name} に「認証済み」ロールを付与しました。")
        except discord.Forbidden: await interaction.response.send_message("エラー: ロールの付与に失敗しました。Botの権限を確認してください。", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(RoleButtonView())
    print(f"Bot起動完了: {bot.user}")
    print("---------------------------------")

# --- 注意書きとボタンを送信するコマンド ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setup_welcome(ctx):
    view = RoleButtonView()
    embed = discord.Embed(title="ようこそ！", description="""
サーバーへようこそ！主に、すこやかグミが作品の投稿や告知、作業配信をするだけのサーバーです。\n
今のところ皆さんが発信できる場は作業配信中(ボイスチャンネルによるライブ)のチャット欄のみとなります。\n
あまり厳しく取り締まるつもりはないですが、オープンな場としてサーバーの皆さんが快適に安全に過ごせるようにご協力をお願いします！
\n\n以下の規約をよくお読みの上、同意いただける場合は下のボタンを押して、チャンネルの閲覧を開始してください。

\n""", color=discord.Color.blue())
    
    embed.add_field(name="主なルール", value="""\n

1.日本の法律、Discordの規約を順守してください。
特に無修正画像、明らかな未成年のセンシティブなコンテンツを取り扱うとサーバー全体がBANになってしまう可能性があるため絶対に禁止です。\n

2.個人情報の投稿、画像の転載などで他者の権利を侵害しないようにしてください。\n

3.多数の閲覧者が不快になる恐れがあるため、下記のような投稿は禁止です。\n

・同一内容の連投などの迷惑行為。\n
・個人や特定の作品に対する明らかな誹謗中傷。\n
・実写、または写実的すぎるメディアの投稿。\n
・生成AIで作成されたメディアの投稿。\n
・特殊性癖、好き嫌いが大きく分かれそうな性癖(獣〇、凌〇、スカ、NTRなど)に該当しそうな内容の直接的な表現。\n
隠語や伏字にする、画像は必要に応じてモザイクをかける、具体的な描写や特定のキャラ名を出すことを避けるなど、苦手な人へ配慮して表現に注意していただければ問題ありません。\n
・実体験に基づく生々しい投稿。
「抜いた！」「濃いの出た！」などは挨拶なのでOKです。「彼女にパイズリしてもらったけど全然気持ち良くなかった」などと発言した場合、即BANです。\n\n

上記が明らかに守れていな場合は予告なくサーバーからBANさせていただく場合がありますのでご了承ください。\n
上記以外の行動でも管理者が不適切と判断した場合、注意または予告なくBANさせていただく場合があります。\n
""", inline=False)
    
    embed.add_field(name="■投稿内容の取扱いについて", value="""
・創作のアイデアになるもの、シチュエーションやセリフのテキストなどを投稿した場合、そのアイデアの権利を放棄したものとします。\n
すこやかグミが制作中であったり、制作の予定があった内容と被るとトラブルになる可能性があるためです。\n
逆に、アイデアの提供やリクエストと捉えて意図的に描くこともあるかもしれませんが、その作品の著作権は全面的にすこやかグミに帰属します。\n\n

この規約の内容は必要に応じて変更される場合があります。
""", inline=False)

    await ctx.send(embed=embed, view=view)
    print("ウェルカムメッセージとボタンを送信しました。")


# --- ボイスチャンネルの状態変化を監視する処理 ---
@bot.event
async def on_voice_state_update(member, before, after):
    guild = bot.get_guild(GUILD_ID)
    if not guild: return

    host_role = guild.get_role(HOST_ROLE_ID)
    if not host_role: print("エラー: 親ロールが見つかりません。"); return
    
    if host_role not in member.roles or before.channel == after.channel:
        return

    viewer_role = guild.get_role(VIEWER_ROLE_ID)
    if not viewer_role: print("エラー: 視聴者ロールが見つかりません。"); return

    vc1 = guild.get_channel(VC1_ID)
    vc2 = guild.get_channel(VC2_ID)
    if not (vc1 and vc2): print("エラー: VC-1またはVC-2が見つかりません。"); return
    
    # --- イベント前後の状態を計算 ---
    hosts_in_vc1_before = len([m for m in vc1.members if host_role in m.roles and m.id != member.id]) + (1 if before.channel == vc1 else 0)
    hosts_in_vc2_before = len([m for m in vc2.members if host_role in m.roles and m.id != member.id]) + (1 if before.channel == vc2 else 0)
    total_hosts_before = hosts_in_vc1_before + hosts_in_vc2_before
    
    hosts_in_vc1_after = len([m for m in vc1.members if host_role in m.roles])
    hosts_in_vc2_after = len([m for m in vc2.members if host_role in m.roles])
    total_hosts_after = hosts_in_vc1_after + hosts_in_vc2_after

    # --- セッション全体の開始・終了を判定 ---
    if total_hosts_before == 0 and total_hosts_after > 0:
        print(f"> 通話セッション開始: ホスト({member.display_name})が入室しました。")
        print("  > 全員に視聴者ロールを付与します。")
        for m in guild.members:
            if host_role not in m.roles and not m.bot and viewer_role not in m.roles:
                try: await m.add_roles(viewer_role)
                except discord.Forbidden: pass
    elif total_hosts_before > 0 and total_hosts_after == 0:
        print(f"> 通話セッション終了: 最後のホスト({member.display_name})が退室しました。")
        print("  > 全員から視聴者ロールを剥奪します。")
        for m in guild.members:
            if viewer_role in m.roles:
                try: await m.remove_roles(viewer_role)
                except discord.Forbidden: pass

    # --- VC-1の管理 ---
    if hosts_in_vc1_before == 0 and hosts_in_vc1_after > 0:
        notification_channel = guild.get_channel(NOTIFICATION_CHANNEL_ID)
        if notification_channel:
            print(f"  > VC-1への初回入室を検知、通知を送信します。")
            try: await notification_channel.send(f"@everyone こんグミ～！すこやかグミが配信開始♥")
            except discord.Forbidden: print("  > エラー: 通知チャンネルへのメッセージ送信権限がありません。")
        print("  > VC-1の接続を許可します。")
        try: await vc1.set_permissions(viewer_role, connect=True)
        except discord.Forbidden: pass
    elif hosts_in_vc1_before > 0 and hosts_in_vc1_after == 0:
        print("  > VC-1の接続を禁止し、視聴者を退出させます。")
        try: await vc1.set_permissions(viewer_role, connect=False)
        except discord.Forbidden: pass
        # ★追加: 強制退出処理
        if before.channel == vc1: # 退出したチャンネルがVC1の場合のみ実行
            for m in before.channel.members:
                if host_role not in m.roles:
                    try:
                        await m.move_to(None, reason="ホストが全員退出しました。")
                        print(f"    - {m.display_name} をVC-1から退出させました。")
                    except discord.Forbidden:
                        print(f"    - エラー: {m.display_name} を退出させられませんでした(権限不足)。")

    # --- VC-2の管理 ---
    if hosts_in_vc2_before == 0 and hosts_in_vc2_after > 0:
        print("  > VC-2の接続を許可します。")
        try: await vc2.set_permissions(viewer_role, connect=True)
        except discord.Forbidden: pass
    elif hosts_in_vc2_before > 0 and hosts_in_vc2_after == 0:
        print("  > VC-2の接続を禁止し、視聴者を退出させます。")
        try: await vc2.set_permissions(viewer_role, connect=False)
        except discord.Forbidden: pass
        # ★追加: 強制退出処理
        if before.channel == vc2: # 退出したチャンネルがVC2の場合のみ実行
            for m in before.channel.members:
                if host_role not in m.roles:
                    try:
                        await m.move_to(None, reason="ホストが全員退出しました。")
                        print(f"    - {m.display_name} をVC-2から退出させました。")
                    except discord.Forbidden:
                        print(f"    - エラー: {m.display_name} を退出させられませんでした(権限不足)。")

# Botを起動
# 2. 環境変数からトークンを読み込むように変更
bot.run(os.environ.get('DISCORD_BOT_TOKEN'))

# --- この上までをコピー ---

