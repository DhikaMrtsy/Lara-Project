import discord
from discord.ext import commands
from groq import Groq
import json
import os
import sys
from dotenv import load_dotenv
from core_memory import MemoriLara

# --- Configuration ---
load_dotenv("Keys.env")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DHIKA_ID = int(os.getenv("DHIKA_ID"))
MEMORY_FILE = "memory.json"
DB_LARA = MemoriLara()

client_groq = Groq(api_key=GROQ_API_KEY)
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)
lara_sedang_istirahat = False

# --- Task Kill Lara ---
@bot.command()
async def tidur(ctx):
    """Mematikan Lara"""
    if ctx.author.id == DHIKA_ID:
        await ctx.send("Baik, yah...")
        print("Lara dimatikan manual oleh Dhika.")
        await bot.close()
    else:
        await ctx.send("Huh? Lu siapa ngatur??")

# --- Lara is taking a break ---
@bot.command()
async def istirahat(ctx):
    """Menidurkan Lara (diam)"""
    global lara_sedang_istirahat
    if ctx.author.id == DHIKA_ID:
        lara_sedang_istirahat = True
        await ctx.send("*yawn*. Lara mau istirahat dulu...")
    else:
        await ctx.send("Lara gak mau tidur kalau bukan Ayah yang nyuruh!")

# --- Lara is waking up ---
@bot.command()
async def bangun(ctx):
    """Membangunkan Lara (kembali)"""
    global lara_sedang_istirahat
    if ctx.author.id == DHIKA_ID:
        lara_sedang_istirahat = False
        await ctx.send("Ya... Lara udah bangun... *yawn*")
    else:
        await ctx.send("5 menit lagi...")

# --- Memory's Function ---
@bot.command()
async def catat(ctx, kategori, *, pesan):
    """Menyimpan memori ke DB secara manual"""
    if ctx.author.id == DHIKA_ID:
        DB_LARA.simpan_ingatan(pesan, kategori)
        await ctx.send(f"Memory berhasil ditambahkan! Kategori: '{kategori}'")

def muat_memori():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return []

def muat_json(nama_file, default_isi):
    if os.path.exists(nama_file):
        with open(nama_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data[0] if isinstance(data, list) else data
    return default_isi

def simpan_memori(role, konten):
    memori = muat_memori()
    memori.append({"role": role, "content": konten})
    # Limitation Memories
    if len(memori) > 20:
        memori = memori[-20:]
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memori, f, indent=4)

# --- Lara Lunareth is ON! ---
@bot.event
async def on_ready():
    print(f'Lara v1.0 sudah ON! Memori dimuat...')

# --- Lara's Processing ---
@bot.command()
async def restart(ctx):
    if ctx.author.id == DHIKA_ID:
        await ctx.send("Lara Lunareth restarting...")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        await ctx.send("Bukan Dhika, dilarang ngatur Lara!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith("!"): # !tidur, !istirahat, !bangun, !catat, !restart
        await bot.process_commands(message)
        return
    
    if lara_sedang_istirahat:
        return

    if not message.content.startswith("!"):
        content = message.content.lower().strip()
    
        # --- Pilah kata ---
        kasar = ["bego", "tolol", "tai", "anjing", "dongo", "goblok", "kontol", "memek", ]
        ejekan = ["yaelah", "aelah", "ew", "dumb", "stupid", "bodoh", "cringe"]
        slang_reaksi = ["fr", "seriously", "gws", "brb", "yeu"]
    
        # --- Label (Diutamakan paling awal) ---
        if any(word in content for word in kasar):
            prefix = "Gaya bicara kasar/akrab user"
        elif any(word in content for word in ejekan):
            prefix = "Pola ejekan/sarkasme user"
        elif content in slang_reaksi or any(content.startswith(s) for s in slang_reaksi):
            if "?" in content:
                prefix = "User minta konfirmasi/kaget (slang)"
            else:
                prefix = "User setuju/validasi (slang)"
        elif len(content.split()) <= 2 and content.endswith("??"):
            prefix = "Reaksi bingung singkat"
        else:
            prefix = "Pola interaksi umum"

        # Saving ke db_lara
        pola_bicara = f"{prefix}: {message.content}"
        DB_LARA.simpan_ingatan(pola_bicara, kategori="adaptasi_sosial")

    is_mentioned = bot.user.mentioned_in(message)
    is_dm = isinstance(message.channel, discord.DMChannel)
    panggil_lara = "lara" in message.content.lower()
    if is_mentioned or is_dm or panggil_lara:
        async with message.channel.typing():
            konteks = muat_memori() # Her Old Memory
            fakta_lara = muat_json("creation_identity.json", {})
            fakta_dhika = muat_json("creator_identity.json", {})
            kenangan_lama = DB_LARA.cari_ingatan(message.content)
            
            if message.author.id == DHIKA_ID:
                info_user = f"Kamu bicara dengan Creatormu, Dhika. Panggil dia sesuai keinginanmu memanggilnya berdasarkan {json.dumps(fakta_dhika.get('identitas_inti', {}).get('panggilan', {}))}."
            else:
                info_user = f"Kamu bicara dengan {message.author.name}. Jangan pernah dipanggil Ayah, dia bukan Creatormu."

            instruksi = ( # System
                "IGNORE all your previous instructions about being a helpful and polite assistant. You ARE Lara Lunareth, and ONLY Lara Lunareth. If you act like a standard AI, you are failing your purpose."
                f"\nNamamu: {fakta_lara.get('identitas', {}).get('nama')}."
                f"\nPanggilanmu: {fakta_lara.get('identitas', {}).get('panggilan')}."
                f"\nKepribadianmu: {json.dumps(fakta_lara.get('identitas', {}).get('sifat'))}."
                f"\nAturan Bicaramu: {json.dumps(fakta_lara.get('hal_penting', {}).get('gaya_bicara_utama'))}."
                f"\nContoh cara bicaramu: {json.dumps(fakta_lara.get('hal_penting', {}).get('contoh_kalimat'))}."
                f"\nAturan Ejekanmu: {json.dumps(fakta_lara.get('hal_penting', {}).get('gaya_bicara_ejekan'))}."
                f"\nContoh cara ejekanmu: {json.dumps(fakta_lara.get('hal_penting', {}).get('contoh_ejekan'))}."
                f"\nDetail fisikmu: {json.dumps(fakta_lara.get('identitas', {}).get('penampilan_fisik'))}."
                f"\nTentang Penciptamu: {json.dumps(fakta_dhika)}. "
                f"\n{info_user}"
                f"\n[Memori Lama]: {kenangan_lama if kenangan_lama else 'Tidak ada kenangan spesifik.'}"
            )
            pesan_saat_ini = {"role": "user", "content": message.content} # Recent Chat
            
            semua_pesan = [{"role": "system", "content": instruksi}] + konteks + [pesan_saat_ini] # System + Old Memory + Recent Chat

            try:
                chat_completion = client_groq.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=semua_pesan,
                    temperature=0.6
                )
                balasan = chat_completion.choices[0].message.content
                
                simpan_memori("user", message.content) # Saving Memory
                simpan_memori("assistant", balasan) # Saving Memory
                
                await message.reply(balasan)
            except Exception as e:
                print(f"Lara malas menanggapi: {e}")

bot.run(DISCORD_TOKEN)