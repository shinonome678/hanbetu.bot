print("--- 完全に新しいファイル bot_v2.py で起動中 ---")
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

VIEWER_ROLE_ID = 1409164397242355724     # 視聴者ロール
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
    viewer_role = guild.get_role(VIEWER_ROLE_ID)
    if not host_role or not viewer_role: 
        print("エラー: ロールが見つかりません。")
        return
    
    # 1. ホスト以外の動き、または同じチャンネル内での状態変化（マイクON/OFFなど）は無視
    if host_role not in member.roles or before.channel == after.channel:
        return

    vc1 = guild.get_channel(VC1_ID)
    vc2 = guild.get_channel(VC2_ID)
    if not (vc1 and vc2): 
        print("エラー: チャンネルが見つかりません。")
        return

    # 現在の各VCにいるホストの数を取得
    hosts_in_vc1 = len([m for m in vc1.members if host_role in m.roles])
    hosts_in_vc2 = len([m for m in vc2.members if host_role in m.roles])

    # --- VC-1 の管理 ---
    # ホストが一人目として入室した場合
    if before.channel != vc1 and after.channel == vc1 and hosts_in_vc1 == 1:
        print(f"> VC-1 配信開始 ({member.display_name})：接続を許可します。")
        # 視聴者ロールに対して「接続」を許可する（一括設定なので429エラーにならない）
        await vc1.set_permissions(viewer_role, connect=True)
        
        notification_channel = guild.get_channel(NOTIFICATION_CHANNEL_ID)
        if notification_channel:
            try: await notification_channel.send(f"@everyone こんグミ～！すこやかグミが配信開始♥")
            except: pass

    # ホストが最後の一人として退室した場合
    elif before.channel == vc1 and after.channel != vc1 and hosts_in_vc1 == 0:
        print(f"> VC-1 配信終了 ({member.display_name})：接続を禁止し、視聴者を退出させます。")
        # 視聴者ロールに対して「接続」を禁止する
        await vc1.set_permissions(viewer_role, connect=False)
        # VC-1に残っている視聴者を強制退出（キック）させる
        for m in vc1.members:
            if host_role not in m.roles:
                try: await m.move_to(None, reason="配信が終了しました。")
                except: pass

    # --- VC-2 の管理 ---
    # ホストが一人目として入室した場合
    if before.channel != vc2 and after.channel == vc2 and hosts_in_vc2 == 1:
        print(f"> VC-2 稼働開始 ({member.display_name})：接続を許可します。")
        await vc2.set_permissions(viewer_role, connect=True)

    # ホストが最後の一人として退室した場合
    elif before.channel == vc2 and after.channel != vc2 and hosts_in_vc2 == 0:
        print(f"> VC-2 稼働終了 ({member.display_name})：接続を禁止し、視聴者を退出させます。")
        await vc2.set_permissions(viewer_role, connect=False)
        for m in vc2.members:
            if host_role not in m.roles:
                try: await m.move_to(None, reason="ホストが退出しました。")
                except: pass
# Botを起動
# 2. 環境変数からトークンを読み込むように変更
bot.run(os.environ.get('DISCORD_BOT_TOKEN'))

# --- この上までをコピー ---


