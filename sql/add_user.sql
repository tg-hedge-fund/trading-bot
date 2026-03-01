-- Insert new user with Argon2 hashed password
-- Username: pranavbhanot
-- Name: pranav
-- Email: pranavbhanot5@gmail.com
-- Password: pranavBh@not@2002
-- Argon2 hash (m=65536, t=2, p=4): $argon2id$v=19$m=65536,t=2,p=4$jmOn1NdWQA5L0mx6p4Nu+w$u1DEeeD6fVXypV/RyPHa1A

INSERT INTO "primary".users (username, email, password_hash)
VALUES (
    'prathmesh',
    '@gmail.com',
    '$argon2id$v=19$m=65536,t=2,p=4$YFD4pMBwChcx48ApJ5nVUg$rUKLuJJgrnwYH/sx5LLvpg'
);
