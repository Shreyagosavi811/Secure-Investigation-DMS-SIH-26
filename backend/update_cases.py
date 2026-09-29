import sqlite3
conn = sqlite3.connect('D:/Antigravity/SIH-26-Criminal-Network-Analysis/backend/demo_sih26190.db')
conn.execute('UPDATE cases SET title="Operation Black Money (Delhi)" WHERE case_id="CASE-2026-001"')
conn.execute('UPDATE cases SET title="Jamtara Cyber Fraud Syndicate" WHERE case_id="CASE-2026-002"')
conn.execute('UPDATE cases SET title="Mumbai Port Narcotics Route" WHERE case_id="CASE-2026-003"')
conn.execute('UPDATE cases SET title="Bollywood VIP Extortion Case" WHERE case_id="CASE-2026-004"')
conn.commit()
conn.close()
