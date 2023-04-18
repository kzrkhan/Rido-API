from realtime.connection import Socket
import os
from typing import List

#WORK IN PROGRESS. WEBHOKS WILL BE IMPLEMENTED IN FUTURE ITERATION OF RIDO FOR ENHANCED PERFORMANCE

# Initialize a Supabase client with your Supabase project URL and API key
SUPABASE_ID = ""
API_KEY: str = os.environ.get("RIDO_DB_KEY")

# Define a function to handle changes in the table
def handle_changes(payload):
    print("Received change:", payload)

if __name__ == "__main__":
    URL = f"wss://{SUPABASE_ID}.supabase.co/realtime/v1/websocket?apikey={API_KEY}&vsn=1.0.0"
    s = Socket(URL)
    s.connect()

    channel_1 = s.set_channel("realtime:*")
    channel_1.join().on("UPDATE", handle_changes)
    s.listen()