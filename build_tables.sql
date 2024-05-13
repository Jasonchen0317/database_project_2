-- CREATE TABLE project_schema.Users (
--     UserID SERIAL PRIMARY KEY,
--     UserName VARCHAR(100),
--     Password VARCHAR(100),
--     Address VARCHAR(255),
--     Latitude DECIMAL(9,6),
--     Longitude DECIMAL(9,6),
--     Profile TEXT,
--     photo BYTEA
-- );

CREATE TABLE project_schema.UserActivity (
    UserID INT UNIQUE REFERENCES Users(UserID),
    LastAccessTimestamp TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES project_schema.Users(UserID)
);

-- CREATE TABLE project_schema.Neighborhoods (
--     NeighborhoodID SERIAL PRIMARY KEY,
--     Name VARCHAR(100)
-- );

-- CREATE TABLE project_schema.Blocks (
--     BlockID SERIAL PRIMARY KEY,
--     Name VARCHAR(100),
--     CenterLatitude DECIMAL(9,6),
--     CenterLongitude DECIMAL(9,6),
--     Radius DECIMAL(5,2),
--     NeighborhoodID INT REFERENCES project_schema.Neighborhoods(NeighborhoodID)
-- );

-- CREATE TABLE project_schema.UserBlocks (
--     UserID INT REFERENCES project_schema.Users(UserID),
--     BlockID INT REFERENCES project_schema.Blocks(BlockID),
--     IsJoined BOOLEAN,
--     PRIMARY KEY (UserID, BlockID)
-- );

-- CREATE TABLE project_schema.BlockRequests (
--     RequestID SERIAL PRIMARY KEY,
--     SenderID INT REFERENCES project_schema.Users(UserID),
--     BlockID INT REFERENCES project_schema.Blocks(BlockID),
--     ApprovedCount INT
-- );

-- CREATE TABLE project_schema.RequestApprovals (
--     ApprovalID SERIAL PRIMARY KEY,
--     RequestID INT REFERENCES project_schema.BlockRequests(RequestID),
--     ApproverID INT REFERENCES project_schema.Users(UserID),
--     UNIQUE(RequestID, ApproverID)
-- );

-- CREATE TABLE project_schema.UserFriends (
--     UserID1 INT,
--     UserID2 INT,
--     FOREIGN KEY (UserID1) REFERENCES project_schema.Users(UserID),
--     FOREIGN KEY (UserID2) REFERENCES project_schema.Users(UserID),
--     PRIMARY KEY (UserID1, UserID2)
-- );

-- CREATE TYPE project_schema.status AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED');

-- CREATE TABLE project_schema.FriendRequests (
--     RequestID SERIAL PRIMARY KEY,
--     SenderID INT REFERENCES project_schema.Users(UserID),
--     ReceiverID INT REFERENCES project_schema.Users(UserID),
-- 	RequestStatus status
-- );

-- CREATE TABLE project_schema.UserNeighbors (
--     UserID1 INT,
--     UserID2 INT,
--     FOREIGN KEY (UserID1) REFERENCES project_schema.Users(UserID),
--     FOREIGN KEY (UserID2) REFERENCES project_schema.Users(UserID),
--     PRIMARY KEY (UserID1, UserID2)
-- );

-- CREATE TYPE project_schema.target AS ENUM ('friend', 'neighbor', 'hood', 'block');

-- CREATE TABLE project_schema.Threads (
--     ThreadID SERIAL PRIMARY KEY,
-- 	Title VARCHAR(255),
--     LocationLatitude DECIMAL(9,6),
--     LocationLongitude DECIMAL(9,6),
-- 	RecipientID INT REFERENCES project_schema.Users(UserID),
-- 	Target target
-- );

-- CREATE TABLE project_schema.Messages (
--     MessageID SERIAL PRIMARY KEY,
--     ThreadID INT REFERENCES project_schema.Threads(ThreadID),
--     AuthorID INT REFERENCES project_schema.Users(UserID),
--     Timestamp TIMESTAMP,
--     Body TEXT
-- );


