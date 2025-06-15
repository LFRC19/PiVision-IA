from db import Database

db = Database()
events = db.get_events(limit=10)
print("Últimos eventos:")
for e in events:
    print(f"{e['timestamp']} | Cam {e['camera_id']} | {e['event_type']} | ID={e['person_id']} conf={e['confidence']:.2f}")
