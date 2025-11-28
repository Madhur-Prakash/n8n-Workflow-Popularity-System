import os
import requests
from dotenv import load_dotenv 
 
load_dotenv() 
    
LOGGER_SERVICE = 'composio'
LOGGER_INTEGRATION = 'composio log'

def logger(service, integration, level, priority, message):
    try:
        res = requests.post( 
            "http://localhost:1027/logger/log",
            json={
                "account_id": os.getenv("WATCHMAN_ACCOUNT_ID"),
                "service": service,
                "integration": integration,
                "level": level,
                "priority": priority,
                "message": message
            },
            headers={
                "WATCHMAN-API-KEY": os.getenv("WATCHMAN_ACCESS_TOKEN"),
                "Content-Type": "application/json"
            },
            timeout=5
        )
        return res.status_code == 200
    except Exception as e:
        print(f"Logger error: {e}")
        return False


if __name__ == "__main__":
    logger(LOGGER_SERVICE, LOGGER_INTEGRATION, "INFO", "null", "Starting email drafting process")



# import mmh3
# import math
# import time


# class CountingBloomFilter:
#     def __init__(self, capacity: int, error_rate: float):
#         self.capacity = capacity
#         self.error_rate = error_rate
#         self.size = self._get_size(capacity, error_rate)
#         self.hash_count = self._get_hash_count(self.size, capacity)
#         self.array = [0] * self.size

#     def _get_size(self, n, p):
#         # m = -(n * ln(p)) / (ln(2)^2)
#         m = -(n * math.log(p)) / (math.log(2) ** 2)
#         return int(m)

#     def _get_hash_count(self, m, n):
#         # k = (m/n) * ln(2)
#         k = (m / n) * math.log(2)
#         return int(k)

#     def _get_hashes(self, item: str):
#         return [mmh3.hash(item, seed) % self.size for seed in range(self.hash_count)]

#     def add(self, item: str):
#         for index in self._get_hashes(item):
#             self.array[index] += 1

#     def remove(self, item: str):
#         if not self.contains(item):
#             return False
#         for index in self._get_hashes(item):
#             self.array[index] -= 1
#         return True

#     def contains(self, item: str) -> bool:
#         st = time.perf_counter()
#         result = all(self.array[index] > 0 for index in self._get_hashes(item))
#         et = time.perf_counter()
#         print(f"Time taken to check membership for '{item}': {et - st} milliseconds")
#         return result


# def delete_user(email: str, phone: str):
#     removed_email = email_filter.remove(email)
#     removed_phone = phone_filter.remove(phone)
#     if removed_email and removed_phone:
#         print("User deleted and Bloom filter cleaned.")
#     else:
#         print("User was not in Bloom filter.")