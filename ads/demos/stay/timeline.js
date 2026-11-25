window.DEMO = {
 "app": "StayFlow",
 "accent": "#A78BFA",
 "icon": "🛏️",
 "audience": "For hotels, resorts & rentals",
 "tagline": "Direct bookings, with an AI booking agent.",
 "steps": [
  {
   "type": "intro",
   "text": "This is StayFlow: direct bookings for hotels, resorts and rentals, with an AI booking agent. Let's follow one booking, from your guest's phone to your dashboard.",
   "say": "This is Stay Flow. Direct bookings for hotels, resorts and rentals, with an AI booking agent. Let's follow one booking, from your guest's phone, to your dashboard.",
   "voice": "voice/00.wav",
   "voice_len": 10.042,
   "start": 0.0,
   "dur": 11.342
  },
  {
   "role": "customer",
   "title": "Your own booking website",
   "text": "Guests book on your own website, with your rooms, rates and photos. No booking fees.",
   "frames": [
    "home",
    "home-2"
   ],
   "voice": "voice/01.wav",
   "voice_len": 4.565,
   "start": 11.342,
   "dur": 5.865
  },
  {
   "role": "customer",
   "title": "Live availability",
   "text": "They add their dates and see which rooms are free, with the price per night.",
   "frames": [
    "rooms",
    "room"
   ],
   "voice": "voice/02.wav",
   "voice_len": 3.437,
   "start": 17.207,
   "dur": 4.8
  },
  {
   "role": "customer",
   "title": "Request a stay",
   "text": "They send a request with their name and number. Nothing is charged, and nothing is booked yet.",
   "frames": [
    "req-form",
    "req-send",
    "req-sent"
   ],
   "voice": "voice/03.wav",
   "voice_len": 5.211,
   "start": 22.007,
   "dur": 7.2
  },
  {
   "type": "explain",
   "role": "customer",
   "title": "Your AI booking agent",
   "text": "Prefer to chat? The AI booking agent checks your live availability, quotes the total, and prepares the request. Nothing is booked until you approve it.",
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
   "voice": "voice/04.wav",
   "voice_len": 9.339,
   "start": 29.207,
   "dur": 10.639
  },
  {
   "role": "owner",
   "title": "Approve with one tap",
   "text": "On your dashboard, every request waits for you. Check the dates, then tap Approve.",
   "frames": [
    "admin",
    "admin-approve",
    "admin-approved"
   ],
   "voice": "voice/05.wav",
   "voice_len": 4.444,
   "start": 39.846,
   "dur": 7.2
  },
  {
   "role": "customer",
   "title": "Booking page & downpayment",
   "text": "Your guest's booking page shows the confirmed stay, and how to pay the downpayment by GCash or bank transfer.",
   "say": "Your guest's booking page shows the confirmed stay, and how to pay the downpayment, by G Cash or bank transfer.",
   "frames": [
    "stay-page"
   ],
   "voice": "voice/06.wav",
   "voice_len": 6.499,
   "start": 47.046,
   "dur": 7.799
  },
  {
   "role": "customer",
   "title": "No double bookings",
   "text": "If someone else tries to book the same room for the same dates, StayFlow stops it. No more double bookings.",
   "say": "If someone else tries to book the same room for the same dates, Stay Flow stops it. No more double bookings.",
   "frames": [
    "clash-send",
    "clash-blocked"
   ],
   "voice": "voice/07.wav",
   "voice_len": 5.946,
   "start": 54.845,
   "dur": 7.246
  },
  {
   "type": "explain",
   "role": "owner",
   "title": "Your AI owner assistant",
   "text": "Need a quick change? Ask your owner assistant to update a rate, or to approve or decline requests. It prepares each action, and it only runs when you tap Confirm.",
   "rows": [
    {
     "icon": "🧑‍💼",
     "who": "You ask",
     "head": "Type it like a message",
     "quote": "Set the Barkada Loft rate to ₱4,800"
    },
    {
     "icon": "✨",
     "who": "Owner assistant",
     "head": "Prepares the change",
     "sub": "Rates, approvals, declines and cancellations."
    },
    {
     "icon": "✅",
     "who": "You decide",
     "head": "It only runs when you confirm",
     "btn": "✓ Confirm",
     "me": true
    }
   ],
   "voice": "voice/08.wav",
   "voice_len": 10.185,
   "start": 62.091,
   "dur": 11.485
  },
  {
   "type": "outro",
   "text": "StayFlow: direct bookings, with AI that waits for your approval. Book a free consultation. Message us on Facebook, or email dandigital1688@gmail.com.",
   "say": "Stay Flow. Direct bookings, with AI that waits for your approval. Book a free consultation. Message us on Facebook, or email dan digital one six eight eight at gmail dot com.",
   "voice": "voice/09.wav",
   "voice_len": 11.776,
   "start": 73.576,
   "dur": 13.076
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
