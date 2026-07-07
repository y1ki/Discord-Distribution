import sqlite3
from pathlib import Path
from threading import Lock


class Database:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent.parent / "data" / "app.db"
        self.db_path.parent.mkdir(exist_ok=True)
        self.lock = Lock()
        self._init_db()
    
    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT NOT NULL UNIQUE,
                    username TEXT,
                    user_id TEXT,
                    email TEXT,
                    phone TEXT,
                    discriminator TEXT,
                    nitro INTEGER DEFAULT 0,
                    proxy_id INTEGER,
                    tag TEXT DEFAULT '---',
                    guilds_count INTEGER DEFAULT 0,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (proxy_id) REFERENCES proxies(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proxies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    protocol TEXT NOT NULL,
                    login TEXT,
                    password TEXT,
                    status TEXT DEFAULT 'alive',
                    response_time REAL,
                    tag TEXT DEFAULT '---',
                    country TEXT DEFAULT 'UN',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ip, port)
                )
            """)
            
            self._remove_duplicate_proxies(cursor)
            
            default_settings = {
                "show_splash": True,
                "show_empty_video": False,
            }
            for key, value in default_settings.items():
                cursor.execute("SELECT COUNT(*) FROM settings WHERE key = ?", (key,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        "INSERT INTO settings (key, value) VALUES (?, ?)",
                        (key, '1' if value else '0')
                    )
            
            cursor.execute("PRAGMA table_info(accounts)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'guilds_count' not in columns:
                cursor.execute("ALTER TABLE accounts ADD COLUMN guilds_count INTEGER DEFAULT 0")
            if 'dm_channels_count' not in columns:
                cursor.execute("ALTER TABLE accounts ADD COLUMN dm_channels_count INTEGER DEFAULT 0")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS broadcast_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(token, channel_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dead_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT NOT NULL UNIQUE,
                    username TEXT,
                    user_id TEXT,
                    email TEXT,
                    phone TEXT,
                    discriminator TEXT,
                    nitro INTEGER DEFAULT 0,
                    proxy_id INTEGER,
                    tag TEXT DEFAULT '---',
                    moved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS insufficient_rights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT NOT NULL UNIQUE,
                    username TEXT,
                    user_id TEXT,
                    email TEXT,
                    phone TEXT,
                    discriminator TEXT,
                    nitro INTEGER DEFAULT 0,
                    proxy_id INTEGER,
                    tag TEXT DEFAULT '---',
                    moved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
    
    def _remove_duplicate_proxies(self, cursor):
        cursor.execute("""
            DELETE FROM proxies 
            WHERE id NOT IN (
                SELECT MAX(id) 
                FROM proxies 
                GROUP BY ip, port
            )
        """)
    
    def get(self, key, default=None):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                value = row[0]
                if value == '1':
                    return True
                elif value == '0':
                    return False
                return value
            return default
    
    def set(self, key, value):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if isinstance(value, bool):
                value = '1' if value else '0'
            
            cursor.execute("""
                INSERT INTO settings (key, value) 
                VALUES (?, ?) 
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, str(value)))
            
            conn.commit()
            conn.close()
    
    def execute(self, query, params=None):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            result = cursor.fetchall()
            conn.close()
            return result
    
    def fetchall(self, query, params=None):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            conn.close()
            return result
    
    def fetchone(self, query, params=None):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            conn.close()
            return result
    
    def save_proxies(self, proxies: list) -> tuple:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT ip, port FROM proxies")
            existing_proxies = set((row[0], row[1]) for row in cursor.fetchall())
            
            saved_count = 0
            duplicates_count = 0
            
            for proxy in proxies:
                try:
                    key = (proxy.ip, proxy.port)
                    if key in existing_proxies:
                        duplicates_count += 1
                        continue
                    
                    cursor.execute("""
                        INSERT OR IGNORE INTO proxies (ip, port, protocol, login, password, status, response_time, tag, country)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        proxy.ip,
                        proxy.port,
                        proxy.protocol,
                        proxy.login,
                        proxy.password,
                        proxy.status,
                        proxy.response_time,
                        getattr(proxy, 'tag', '---'),
                        getattr(proxy, 'country', 'UN')
                    ))
                    if cursor.rowcount > 0:
                        existing_proxies.add(key)
                        saved_count += 1
                    else:
                        duplicates_count += 1
                except Exception:
                    continue
            
            conn.commit()
            conn.close()
            return saved_count, duplicates_count
    
    def load_proxies(self) -> list:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, ip, port, protocol, login, password, status, response_time, tag, country 
                FROM proxies 
                ORDER BY created_at DESC
            """)
            result = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return result
    
    def get_proxy_count(self) -> int:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM proxies")
            count = cursor.fetchone()[0]
            conn.close()
            return count
    
    def delete_proxies(self, proxy_ids: list) -> int:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            placeholders = ",".join("?" * len(proxy_ids))
            cursor.execute(f"DELETE FROM proxies WHERE id IN ({placeholders})", proxy_ids)
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            return deleted_count
    
    def delete_accounts(self, account_ids: list) -> int:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            placeholders = ",".join("?" * len(account_ids))
            cursor.execute(f"DELETE FROM accounts WHERE id IN ({placeholders})", account_ids)
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            return deleted_count
    
    def remove_duplicate_proxies(self) -> int:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            self._remove_duplicate_proxies(cursor)
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            return deleted_count
    
    def update_proxy_tags(self, proxy_ids: list, tag: str) -> int:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            placeholders = ",".join("?" * len(proxy_ids))
            cursor.execute(f"UPDATE proxies SET tag = ? WHERE id IN ({placeholders})", [tag] + proxy_ids)
            updated_count = cursor.rowcount
            conn.commit()
            conn.close()
            return updated_count
    
    def get_proxy_tags(self) -> list:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT tag FROM proxies WHERE tag != '---' ORDER BY tag")
            tags = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tags
    
    def get_proxy_countries(self) -> list:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT country FROM proxies WHERE country != 'UN' ORDER BY country")
            countries = [row[0] for row in cursor.fetchall()]
            conn.close()
            return countries
    
    def update_proxy_status(self, proxy_id: int, status: str, response_time: float, country: str, protocol: str) -> bool:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE proxies SET status = ?, response_time = ?, country = ?, protocol = ? WHERE id = ?",
                (status, response_time, country, protocol, proxy_id)
            )
            conn.commit()
            conn.close()
            return True
    
    def save_account(self, token: str, username: str, user_id: str, email: str, phone: str,
                    discriminator: str, nitro: int, proxy_id: int, tag: str = "---",
                    guilds_count: int = 0, dm_channels_count: int = 0) -> int:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO accounts 
                (token, username, user_id, email, phone, discriminator, nitro, proxy_id, tag, guilds_count, dm_channels_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (token, username, user_id, email, phone, discriminator, nitro, proxy_id, tag, guilds_count, dm_channels_count))
            account_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return account_id
    
    def get_accounts(self, limit: int = None, offset: int = 0) -> list:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = """
                SELECT a.id, a.token, a.username, a.user_id, a.email, a.phone,
                       a.discriminator, a.nitro, a.proxy_id, a.tag, a.added_date,
                       p.ip, p.port
                FROM accounts a
                LEFT JOIN proxies p ON a.proxy_id = p.id
                ORDER BY a.added_date DESC
            """
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            cursor.execute(query)
            accounts = cursor.fetchall()
            conn.close()
            return accounts
    
    def get_account_count(self) -> int:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM accounts")
            count = cursor.fetchone()[0]
            conn.close()
            return count
    
    def update_account_tag(self, account_id: int, tag: str) -> bool:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE accounts SET tag = ? WHERE id = ?", (tag, account_id))
            conn.commit()
            conn.close()
            return True
    
    def update_account_tags(self, account_ids: list, tag: str) -> int:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            placeholders = ",".join("?" * len(account_ids))
            cursor.execute(f"UPDATE accounts SET tag = ? WHERE id IN ({placeholders})", [tag] + account_ids)
            updated_count = cursor.rowcount
            conn.commit()
            conn.close()
            return updated_count
    
    def update_account_proxy(self, account_id: int, proxy_id: int) -> bool:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE accounts SET proxy_id = ? WHERE id = ?", (proxy_id, account_id))
            conn.commit()
            conn.close()
            return True
    
    def get_proxies_for_rotation(self, mode: str, value: str = None) -> list:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if mode == "all":
                cursor.execute("SELECT * FROM proxies WHERE status = 'alive'")
            elif mode == "tag":
                cursor.execute("SELECT * FROM proxies WHERE tag = ? AND status = 'alive'", (value,))
            elif mode == "country":
                cursor.execute("SELECT * FROM proxies WHERE country = ? AND status = 'alive'", (value,))
            elif mode == "unused":
                cursor.execute("""
                    SELECT * FROM proxies 
                    WHERE status = 'alive' 
                    AND id NOT IN (SELECT DISTINCT proxy_id FROM accounts WHERE proxy_id IS NOT NULL)
                """)
            
            proxies = cursor.fetchall()
            conn.close()
            return proxies
    
    def get_account_tags(self) -> list:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT tag FROM accounts WHERE tag != '---' ORDER BY tag")
            tags = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tags

    def get_accounts_by_tag(self, tag: str) -> list:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, a.token, a.username, a.user_id, a.email, a.phone,
                       a.discriminator, a.nitro, a.proxy_id, a.tag,
                       p.ip, p.port, p.protocol, p.login, p.password
                FROM accounts a
                LEFT JOIN proxies p ON a.proxy_id = p.id
                WHERE a.tag = ?
                ORDER BY a.added_date DESC
            """, (tag,))
            rows = cursor.fetchall()
            conn.close()
            return [self._account_row_to_dict(r) for r in rows]

    def get_accounts_with_proxy(self) -> list:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, a.token, a.username, a.user_id, a.email, a.phone,
                       a.discriminator, a.nitro, a.proxy_id, a.tag,
                       p.ip, p.port, p.protocol, p.login, p.password
                FROM accounts a
                LEFT JOIN proxies p ON a.proxy_id = p.id
                ORDER BY a.added_date DESC
            """)
            rows = cursor.fetchall()
            conn.close()
            return [self._account_row_to_dict(r) for r in rows]

    def _account_row_to_dict(self, row) -> dict:
        return {
            "id": row[0],
            "token": row[1],
            "username": row[2],
            "user_id": row[3],
            "email": row[4],
            "phone": row[5],
            "discriminator": row[6],
            "nitro": row[7],
            "proxy_id": row[8],
            "tag": row[9],
            "proxy": {
                "ip": row[10],
                "port": row[11],
                "protocol": row[12],
                "login": row[13],
                "password": row[14],
            } if row[10] else None
        }

    def get_sent_channels(self, token: str) -> set:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT channel_id FROM broadcast_history WHERE token = ?", (token,))
            result = {row[0] for row in cursor.fetchall()}
            conn.close()
            return result

    def save_sent_channel(self, token: str, channel_id: str):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO broadcast_history (token, channel_id) VALUES (?, ?)",
                (token, channel_id)
            )
            conn.commit()
            conn.close()

    def clear_broadcast_history(self):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM broadcast_history")
            conn.commit()
            conn.close()

    def move_to_dead(self, account_ids: list):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            placeholders = ','.join('?' for _ in account_ids)
            cursor.execute(f"""
                INSERT OR IGNORE INTO dead_tokens
                    (token, username, user_id, email, phone, discriminator, nitro, proxy_id, tag)
                SELECT token, username, user_id, email, phone, discriminator, nitro, proxy_id, tag
                FROM accounts WHERE id IN ({placeholders})
            """, account_ids)
            cursor.execute(f"DELETE FROM accounts WHERE id IN ({placeholders})", account_ids)
            conn.commit()
            conn.close()

    def get_dead_tokens(self) -> list:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id, d.token, d.username, d.user_id, d.email, d.phone,
                       d.discriminator, d.nitro, d.proxy_id, d.tag, d.moved_date,
                       p.ip, p.port
                FROM dead_tokens d
                LEFT JOIN proxies p ON d.proxy_id = p.id
                ORDER BY d.moved_date DESC
            """)
            rows = cursor.fetchall()
            conn.close()
            return [tuple(r) for r in rows]

    def get_dead_tokens_count(self) -> int:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM dead_tokens")
            count = cursor.fetchone()[0]
            conn.close()
            return count

    def delete_dead_tokens(self, ids: list):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            placeholders = ','.join('?' for _ in ids)
            cursor.execute(f"DELETE FROM dead_tokens WHERE id IN ({placeholders})", ids)
            conn.commit()
            conn.close()

    def restore_dead_tokens(self, ids: list):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            placeholders = ','.join('?' for _ in ids)
            cursor.execute(f"""
                INSERT OR IGNORE INTO accounts
                    (token, username, user_id, email, phone, discriminator, nitro, proxy_id, tag)
                SELECT token, username, user_id, email, phone, discriminator, nitro, proxy_id, tag
                FROM dead_tokens WHERE id IN ({placeholders})
            """, ids)
            cursor.execute(f"DELETE FROM dead_tokens WHERE id IN ({placeholders})", ids)
            conn.commit()
            conn.close()

    def move_to_insufficient_rights(self, account_ids: list):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            placeholders = ','.join('?' for _ in account_ids)
            cursor.execute(f"""
                INSERT OR IGNORE INTO insufficient_rights
                    (token, username, user_id, email, phone, discriminator, nitro, proxy_id, tag)
                SELECT token, username, user_id, email, phone, discriminator, nitro, proxy_id, tag
                FROM accounts WHERE id IN ({placeholders})
            """, account_ids)
            cursor.execute(f"DELETE FROM accounts WHERE id IN ({placeholders})", account_ids)
            conn.commit()
            conn.close()

    def get_insufficient_rights(self) -> list:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.id, d.token, d.username, d.user_id, d.email, d.phone,
                       d.discriminator, d.nitro, d.proxy_id, d.tag, d.moved_date,
                       p.ip, p.port
                FROM insufficient_rights d
                LEFT JOIN proxies p ON d.proxy_id = p.id
                ORDER BY d.moved_date DESC
            """)
            rows = cursor.fetchall()
            conn.close()
            return [tuple(r) for r in rows]

    def get_insufficient_rights_count(self) -> int:
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM insufficient_rights")
            count = cursor.fetchone()[0]
            conn.close()
            return count

    def delete_insufficient_rights(self, ids: list):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            placeholders = ','.join('?' for _ in ids)
            cursor.execute(f"DELETE FROM insufficient_rights WHERE id IN ({placeholders})", ids)
            conn.commit()
            conn.close()

    def restore_insufficient_rights(self, ids: list):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            placeholders = ','.join('?' for _ in ids)
            cursor.execute(f"""
                INSERT OR IGNORE INTO accounts
                    (token, username, user_id, email, phone, discriminator, nitro, proxy_id, tag)
                SELECT token, username, user_id, email, phone, discriminator, nitro, proxy_id, tag
                FROM insufficient_rights WHERE id IN ({placeholders})
            """, ids)
            cursor.execute(f"DELETE FROM insufficient_rights WHERE id IN ({placeholders})", ids)
            conn.commit()
            conn.close()

    def get_proxy_sort_state(self) -> int:
        return int(self.get("proxy_ping_sort", 0))

    def set_proxy_sort_state(self, state: int):
        self.set("proxy_ping_sort", state)
