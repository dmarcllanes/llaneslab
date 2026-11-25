window.DEMO = {
 "app": "StayFlow",
 "accent": "#A78BFA",
 "icon": "🛏️",
 "audience": "For hotels, resorts & rentals",
 "tagline": "Direct bookings, with an AI booking agent.",
 "steps": [
  {
   "type": "intro",
   "text": "StayFlow: direct bookings for hotels, resorts and rentals, with an AI booking agent.",
   "say": "Stay Flow. Direct bookings for hotels, resorts and rentals, with an AI booking agent.",
   "voice": "voice-60s/00.wav",
   "voice_len": 5.477,
   "start": 0.0,
   "dur": 8.189
  },
  {
   "role": "customer",
   "title": "Your own booking website",
   "text": "Guests book on your own website, and see which rooms are free for their dates.",
   "frames": [
    "home",
    "rooms"
   ],
   "voice": "voice-60s/01.wav",
   "voice_len": 3.748,
   "start": 8.189,
   "dur": 6.46
  },
  {
   "role": "customer",
   "title": "Request a stay",
   "text": "They send a request. Nothing is charged, and nothing is booked yet.",
   "frames": [
    "req-send",
    "req-sent"
   ],
   "voice": "voice-60s/02.wav",
   "voice_len": 3.625,
   "start": 14.649,
   "dur": 6.337
  },
  {
   "type": "explain",
   "role": "customer",
   "title": "Your AI booking agent",
   "text": "Prefer to chat? The AI booking agent checks availability and prepares the request for you to approve.",
   "rows": [
    {
     "icon": "💬",
     "who": "Guest asks",
     "head": "Any time, in their own words",
     "quote": "A room for 4 this Saturday?"
    },
    {
     "icon": "📅",
     "who": "AI booking agent",
     "head": "Checks live availability",
     "sub": "Quotes the total and prepares the stay request. The guest taps Send request."
    },
    {
     "icon": "✅",
     "who": "You decide",
     "head": "Nothing is booked until you approve",
     "btn": "✓ Approve",
     "me": true
    }
   ],
   "voice": "voice-60s/03.wav",
   "voice_len": 6.232,
   "start": 20.986,
   "dur": 8.944
  },
  {
   "role": "owner",
   "title": "Approve with one tap",
   "text": "On your dashboard, check the dates and tap Approve.",
   "frames": [
    "admin-approve",
    "admin-approved"
   ],
   "voice": "voice-60s/04.wav",
   "voice_len": 2.563,
   "start": 29.93,
   "dur": 6.212
  },
  {
   "role": "customer",
   "title": "Booking page & downpayment",
   "text": "Your guest's page shows the confirmed stay and how to pay the downpayment.",
   "frames": [
    "stay-page"
   ],
   "voice": "voice-60s/05.wav",
   "voice_len": 3.977,
   "start": 36.142,
   "dur": 6.689
  },
  {
   "role": "customer",
   "title": "No double bookings",
   "text": "Same room, same dates? StayFlow stops it.",
   "say": "Same room, same dates? Stay Flow stops it.",
   "frames": [
    "clash-send",
    "clash-blocked"
   ],
   "voice": "voice-60s/06.wav",
   "voice_len": 2.543,
   "start": 42.831,
   "dur": 6.212
  },
  {
   "type": "outro",
   "text": "StayFlow: direct bookings, with AI that waits for your approval. Book a free consultation. Message us on Facebook, or email dandigital1688@gmail.com.",
   "say": "Stay Flow. Book a free consultation. Message us on Facebook, or email dan digital one six eight eight at gmail dot com.",
   "voice": "voice-60s/07.wav",
   "voice_len": 8.241,
   "start": 49.043,
   "dur": 10.957
  }
 ],
 "shots": {
  "home": {
   "src": "shots/home.png"
  },
  "home-2": {
   "src": "shots/home-2.png"
  },
  "rooms": {
   "src": "shots/rooms.png"
  },
  "room": {
   "src": "shots/room.png"
  },
  "req-form": {
   "src": "shots/req-form.png"
  },
  "req-send": {
   "src": "shots/req-send.png",
   "tap": [
    195,
    422
   ]
  },
  "req-sent": {
   "src": "shots/req-sent.png"
  },
  "admin": {
   "src": "shots/admin.png"
  },
  "admin-approve": {
   "src": "shots/admin-approve.png",
   "tap": [
    215,
    697
   ]
  },
  "admin-approved": {
   "src": "shots/admin-approved.png"
  },
  "slip": {
   "src": "shots/slip.png"
  },
  "stay-page": {
   "src": "shots/stay-page.png"
  },
  "clash-send": {
   "src": "shots/clash-send.png",
   "tap": [
    195,
    522
   ]
  },
  "clash-blocked": {
   "src": "shots/clash-blocked.png"
  }
 }
};
