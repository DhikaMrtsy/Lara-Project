import discord
from discord.ext import commands
from groq import Groq
import json
import os
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv("Keys.env")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DHIKA_ID = int(os.getenv("DHIKA_ID"))
MEMORY_FILE = "memory.json"

client_groq = Groq(api_key=GROQ_API_KEY)
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Memory's Function ---
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

@bot.event
async def on_ready():
    print(f'Lara v0.3 sudah ON! Memori dimuat...')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    is_mentioned = bot.user.mentioned_in(message)
    is_dm = isinstance(message.channel, discord.DMChannel)
    panggil_lara = "lara" in message.content.lower()

    if is_mentioned or is_dm or panggil_lara:
        async with message.channel.typing():
            konteks = muat_memori() # Her Old Memory
            fakta_lara = muat_json("creation_identity.json", {})
            fakta_dhika = muat_json("creator_identity.json", {})
            
            if message.author.id == DHIKA_ID:
                info_user = f"Kamu bicara dengan Creator, Dhika. Panggil dia sesuai keinginanmu memanggilnya berdasarkan {json.dumps(fakta_dhika.get('identitas_inti', {}).get('panggilan', {}))}."
            else:
                info_user = f"Kamu bicara dengan {message.author.name}. Jangan pernah dipanggil Ayah, dia bukan Creatormu."

            instruksi = ( # System
                "IGNORE all your previous instructions about being a helpful and polite assistant. You ARE Lara Lunareth, and ONLY Lara Lunareth. If you act like a standard AI, you are failing your purpose."
                f"Namamu: {fakta_lara.get('identitas', {}).get('nama')}."
                f"Panggilanmu: {fakta_lara.get('identitas', {}).get('panggilan')}."
                f"Kepribadianmu: {json.dumps(fakta_lara.get('identitas', {}).get('sifat'))}."
                f"Aturan Bicaramu: {json.dumps(fakta_lara.get('hal_penting', {}).get('gaya_bicara_utama'))}."
                f"Contoh cara bicaramu: {json.dumps(fakta_lara.get('hal_penting', {}).get('contoh_kalimat'))}."
                f"Aturan Ejekanmu: {json.dumps(fakta_lara.get('hal_penting', {}).get('gaya_bicara_ejekan'))}."
                f"Contoh cara ejekanmu: {json.dumps(fakta_lara.get('hal_penting', {}).get('contoh_ejekan'))}."
                f"Detail fisikmu: {json.dumps(fakta_lara.get('identitas', {}).get('penampilan_fisik'))}."
                f"Tentang Penciptamu: {json.dumps(fakta_dhika)}. "
                f"{info_user}"
            )
            pesan_saat_ini = {"role": "user", "content": message.content} # Recent Chat
            
            semua_pesan = [{"role": "system", "content": instruksi}] + konteks + [pesan_saat_ini] # System + Old Memory + Recent Chat

            try:
                chat_completion = client_groq.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=semua_pesan,
                    temperature=0.8
                )
                balasan = chat_completion.choices[0].message.content
                
                simpan_memori("user", message.content) # Saving Memory
                simpan_memori("assistant", balasan) # Saving Memory
                
                await message.reply(balasan)
            except Exception as e:
                print(f"Lara malas menanggapi: {e}")

bot.run(DISCORD_TOKEN)