window.DEMO = {
 "app": "ShopFlow",
 "accent": "#10B981",
 "icon": "🛍️",
 "audience": "For shops & small businesses",
 "tagline": "Your own online store, with an AI shop assistant.",
 "steps": [
  {
   "type": "intro",
   "text": "ShopFlow: your own online store, with an AI shop assistant. Here's one order, start to finish.",
   "say": "Shop Flow. Your own online store, with an AI shop assistant. Here's one order, start to finish.",
   "voice": "voice-60s/00.wav",
   "voice_len": 5.832,
   "start": 0.0,
   "dur": 8.226
  },
  {
   "role": "customer",
   "title": "Ask the AI shop assistant",
   "text": "Customers ask the AI shop assistant. It checks your real stock and prepares the cart.",
   "frames": [
    "chat-ask",
    "chat-answer",
    "chat-cart"
   ],
   "voice": "voice-60s/01.wav",
   "voice_len": 5.322,
   "start": 8.226,
   "dur": 8.294
  },
  {
   "role": "customer",
   "title": "Check out & pay",
   "text": "They check out, then pay by GCash or bank transfer, or cash on delivery.",
   "say": "They check out, then pay by G Cash or bank transfer, or cash on delivery.",
   "frames": [
    "checkout-filled",
    "order-pay"
   ],
   "voice": "voice-60s/02.wav",
   "voice_len": 4.389,
   "start": 16.52,
   "dur": 6.783
  },
  {
   "role": "customer",
   "title": "Upload the payment screenshot",
   "text": "Then they upload the payment screenshot.",
   "frames": [
    "proof-chosen",
    "proof-sent"
   ],
   "voice": "voice-60s/03.wav",
   "voice_len": 1.75,
   "start": 23.303,
   "dur": 5.894
  },
  {
   "role": "owner",
   "title": "Check the payment",
   "text": "You compare it, and tap Payment received.",
   "frames": [
    "admin-verify",
    "admin-paid"
   ],
   "voice": "voice-60s/04.wav",
   "voice_len": 2.076,
   "start": 29.197,
   "dur": 5.894
  },
  {
   "role": "owner",
   "title": "Your AI store co-pilot",
   "text": "Your co-pilot prepares changes like \"mark as packed\". Nothing happens until you tap Confirm.",
   "say": "Your co-pilot prepares changes, like, mark as packed. Nothing happens until you tap, Confirm.",
   "frames": [
    "copilot-ask",
    "copilot-confirm",
    "copilot-done"
   ],
   "voice": "voice-60s/05.wav",
   "voice_len": 5.729,
   "start": 35.091,
   "dur": 8.294
  },
  {
   "role": "customer",
   "title": "Ship & track",
   "text": "Add the tracking number, and your customer follows every step.",
   "frames": [
    "admin-ship",
    "customer-progress"
   ],
   "voice": "voice-60s/06.wav",
   "voice_len": 3.208,
   "start": 43.385,
   "dur": 5.894
  },
  {
   "type": "outro",
   "text": "ShopFlow: your store, with AI that waits for your approval. Book a free consultation. Message us on Facebook, or email dandigital1688@gmail.com.",
   "say": "Shop Flow. Book a free consultation. Message us on Facebook, or email dan digital one six eight eight at gmail dot com.",
   "voice": "voice-60s/07.wav",
   "voice_len": 8.33,
   "start": 49.279,
   "dur": 10.721
  }
 ],
 "shots": {
  "home": {
   "src": "shots/home.png"
  },
  "home-cats": {
   "src": "shots/home-cats.png"
  },
  "chat-ask": {
   "src": "shots/chat-ask.png",
   "tap": [
    337,
    123
   ]
  },
  "chat-answer": {
   "src": "shots/chat-answer.png"
  },
  "chat-cart": {
   "src": "shots/chat-cart.png",
   "tap": [
    213,
    565
   ]
  },
  "checkout-top": {
   "src": "shots/checkout-top.png"
  },
  "checkout-filled": {
   "src": "shots/checkout-filled.png",
   "tap": [
    195,
    422
   ]
  },
  "order-new": {
   "src": "shots/order-new.png"
  },
  "order-pay": {
   "src": "shots/order-pay.png"
  },
  "proof-chosen": {
   "src": "shots/proof-chosen.png",
   "tap": [
    195,
    422
   ]
  },
  "proof-sent": {
   "src": "shots/proof-sent.png"
  },
  "admin-orders": {
   "src": "shots/admin-orders.png"
  },
  "admin-verify": {
   "src": "shots/admin-verify.png",
   "tap": [
    195,
    629
   ]
  },
  "admin-paid": {
   "src": "shots/admin-paid.png"
  },
  "copilot-ask": {
   "src": "shots/copilot-ask.png",
   "tap": [
    337,
    123
   ]
  },
  "copilot-confirm": {
   "src": "shots/copilot-confirm.png",
   "tap": [
    127,
    331
   ]
  },
  "copilot-done": {
   "src": "shots/copilot-done.png"
  },
  "admin-ship": {
   "src": "shots/admin-ship.png",
   "tap": [
    195,
    629
   ]
  },
  "admin-shipped": {
   "src": "shots/admin-shipped.png"
  },
  "customer-progress": {
   "src": "shots/customer-progress.png"
  }
 }
};
