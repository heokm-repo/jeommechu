-- MySQL 8.x schema for Jeommechu MVP.
-- The server creates DB_NAME if needed, then applies these objects inside that database.

CREATE TABLE IF NOT EXISTS users (
  id CHAR(36) PRIMARY KEY,
  user_type ENUM('GUEST', 'MEMBER') NOT NULL,
  auth_provider ENUM('NONE', 'KAKAO', 'GOOGLE', 'APPLE', 'EMAIL') NOT NULL,
  provider_user_id VARCHAR(255),
  email VARCHAR(255),
  password_hash TEXT,
  status ENUM('ACTIVE', 'DELETED') NOT NULL DEFAULT 'ACTIVE',
  deleted_at DATETIME(6),
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  UNIQUE KEY uq_users_provider_user (auth_provider, provider_user_id),
  KEY idx_users_email (email),
  KEY idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS auth_sessions (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  session_token_hash CHAR(64) NOT NULL UNIQUE,
  expires_at DATETIME(6) NOT NULL,
  revoked_at DATETIME(6),
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  CONSTRAINT fk_auth_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  KEY idx_auth_sessions_user (user_id),
  KEY idx_auth_sessions_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE IF NOT EXISTS search_logs (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36),
  latitude DECIMAL(10, 7),
  longitude DECIMAL(10, 7),
  address_text VARCHAR(500),
  emotion_state VARCHAR(255) NOT NULL,
  search_context TEXT,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  CONSTRAINT fk_search_logs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  KEY idx_search_logs_user_created (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ai_responses (
  id CHAR(36) PRIMARY KEY,
  search_log_id CHAR(36) NOT NULL UNIQUE,
  model_name VARCHAR(100) NOT NULL,
  prompt_text TEXT NOT NULL,
  response_text JSON NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  CONSTRAINT fk_ai_responses_search FOREIGN KEY (search_log_id) REFERENCES search_logs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ai_extracted_keywords (
  id CHAR(36) PRIMARY KEY,
  search_log_id CHAR(36) NOT NULL,
  keyword VARCHAR(255) NOT NULL,
  keyword_type ENUM('MOOD', 'FOOD_TYPE', 'SITUATION', 'PLACE_TYPE') NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  CONSTRAINT fk_ai_keywords_search FOREIGN KEY (search_log_id) REFERENCES search_logs(id) ON DELETE CASCADE,
  KEY idx_ai_keywords_search (search_log_id),
  KEY idx_ai_keywords_keyword (keyword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS restaurants (
  id CHAR(36) PRIMARY KEY,
  external_provider VARCHAR(50) NOT NULL,
  external_place_id VARCHAR(100) NOT NULL,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(255),
  phone VARCHAR(50),
  address VARCHAR(500),
  road_address VARCHAR(500),
  latitude DECIMAL(10, 7),
  longitude DECIMAL(10, 7),
  rating DECIMAL(3, 2),
  review_count INT,
  opening_hours JSON,
  raw_data JSON,
  last_synced_at DATETIME(6) NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  UNIQUE KEY uq_restaurants_external_place (external_provider, external_place_id),
  KEY idx_restaurants_location (latitude, longitude),
  KEY idx_restaurants_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS restaurant_search_cache (
  id CHAR(36) PRIMARY KEY,
  cache_key CHAR(64) NOT NULL UNIQUE,
  query VARCHAR(255) NOT NULL,
  center_latitude DECIMAL(10, 7),
  center_longitude DECIMAL(10, 7),
  radius INT NOT NULL,
  sort VARCHAR(30) NOT NULL DEFAULT 'distance',
  requested_pages INT NOT NULL DEFAULT 1,
  result_count INT NOT NULL DEFAULT 0,
  is_complete BOOLEAN NOT NULL DEFAULT FALSE,
  status ENUM('SUCCESS', 'EMPTY', 'FAILED') NOT NULL,
  raw_response JSON,
  synced_at DATETIME(6) NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  KEY idx_restaurant_search_cache_lookup (query, center_latitude, center_longitude, radius, synced_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS restaurant_sync_logs (
  id CHAR(36) PRIMARY KEY,
  restaurant_id CHAR(36) NOT NULL,
  sync_status ENUM('SUCCESS', 'FAILED') NOT NULL,
  error_message TEXT,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  CONSTRAINT fk_sync_logs_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
  KEY idx_sync_logs_restaurant (restaurant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS search_recommendations (
  id CHAR(36) PRIMARY KEY,
  search_log_id CHAR(36) NOT NULL,
  restaurant_id CHAR(36) NOT NULL,
  recommendation_rank INT NOT NULL,
  score DECIMAL(5, 2) NOT NULL,
  ai_reason TEXT,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  CONSTRAINT fk_recommendations_search FOREIGN KEY (search_log_id) REFERENCES search_logs(id) ON DELETE CASCADE,
  CONSTRAINT fk_recommendations_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
  KEY idx_recommendations_search_rank (search_log_id, recommendation_rank),
  KEY idx_recommendations_restaurant (restaurant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS recommendation_logs (
  id CHAR(36) PRIMARY KEY,
  search_log_id CHAR(36) NOT NULL,
  log_type ENUM('SEARCH', 'CLICK', 'FAVORITE', 'VISIT', 'FEEDBACK') NOT NULL,
  payload JSON NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  CONSTRAINT fk_recommendation_logs_search FOREIGN KEY (search_log_id) REFERENCES search_logs(id) ON DELETE CASCADE,
  KEY idx_recommendation_logs_search_type (search_log_id, log_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS user_favorites (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  restaurant_id CHAR(36) NOT NULL,
  memo TEXT,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  CONSTRAINT fk_favorites_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_favorites_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
  UNIQUE KEY uq_user_favorites_user_restaurant (user_id, restaurant_id),
  KEY idx_favorites_user_created (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS visit_histories (
  id CHAR(36) PRIMARY KEY,
  user_id CHAR(36) NOT NULL,
  restaurant_id CHAR(36) NOT NULL,
  search_log_id CHAR(36),
  rating INT,
  review_text TEXT,
  is_verified BOOLEAN NOT NULL DEFAULT FALSE,
  visited_at DATETIME(6) NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  CONSTRAINT fk_visits_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_visits_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
  CONSTRAINT fk_visits_search FOREIGN KEY (search_log_id) REFERENCES search_logs(id) ON DELETE SET NULL,
  KEY idx_visits_user_visited (user_id, visited_at),
  KEY idx_visits_restaurant (restaurant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS regions (
  id CHAR(36) PRIMARY KEY,
  sido VARCHAR(100) NOT NULL,
  sigungu VARCHAR(100) NOT NULL,
  dong VARCHAR(100) NOT NULL,
  created_at DATETIME(6) NOT NULL,
  updated_at DATETIME(6) NOT NULL,
  UNIQUE KEY uq_regions_sido_sigungu_dong (sido, sigungu, dong)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


