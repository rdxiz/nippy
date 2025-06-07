

class QueueType:
    PROCESS_VIDEO = 1

class RateLimit:
    PROFILE_CREATION = 1
    VIDEO_UPLOAD = 2
    VIEWS = 2
    
    
class VideoResolutions:
    Q_144P = 1
    Q_240P = 2

    CHOICES = [
        (Q_144P, '144p'),
        (Q_240P, "240p"),
    ]
    
    
class VideoCategory:
    FILM_AND_ANIMATION = 1
    AUTOS_AND_VEHICLES = 2
    EDUCATION_AND_INSTRUCTIONAL = 3
    ENTERTAINMENT = 4
    EVENTS_AND_WEDDINGS = 5
    FAMILY = 6
    FOR_SALE_AND_AUCTIONS = 7
    HOBBIES_AND_INTERESTS = 8
    HUMOR = 9
    MUSIC = 10
    NEWS_AND_POLITICS = 11
    ODD_AND_OUTRAGEOUS = 12
    PEOPLE_AND_BLOGS = 13
    PERSONALS_AND_DATING = 14
    PETS_AND_ANIMALS = 15
    SCIENCE_AND_TECHNOLOGY = 16
    SHORT_MOVIES = 17
    SPORTS = 18
    TRAVEL_AND_EVENTS = 19
    GAMING = 20
    VIDEOBLOGGING = 21

    CHOICES = [
        (FILM_AND_ANIMATION, "Film & Animation"),
        (AUTOS_AND_VEHICLES, "Autos & Vehicles"),
        (EDUCATION_AND_INSTRUCTIONAL, "Education & Instructional"),
        (ENTERTAINMENT, "Entertainment"),
        (EVENTS_AND_WEDDINGS, "Events & Weddings"),
        (FAMILY, "Family"),
        (FOR_SALE_AND_AUCTIONS, "For Sale & Auctions"),
        (HOBBIES_AND_INTERESTS, "Hobbies & Interests"),
        (HUMOR, "Humor"),
        (MUSIC, "Music"),
        (NEWS_AND_POLITICS, "News & Politics"),
        (ODD_AND_OUTRAGEOUS, "Odd & Outrageous"),
        (PEOPLE_AND_BLOGS, "People & Blogs"),
        (PERSONALS_AND_DATING, "Personals & Dating"),
        (PETS_AND_ANIMALS, "Pets & Animals"),
        (SCIENCE_AND_TECHNOLOGY, "Science & Technology"),
        (SHORT_MOVIES, "Short Movies"),
        (SPORTS, "Sports"),
        (TRAVEL_AND_EVENTS, "Travel & Events"),
        (GAMING, "Gaming"),
        (VIDEOBLOGGING, "Videoblogging")
    ]


class VideoVisibility:
    PUBLIC = 1
    PRIVATE = 2
    UNLISTED = 3

    CHOICES = [
        (PUBLIC, "Public"),
        (PRIVATE, "Private"),
        (UNLISTED, "Unlisted")
    ]


class CommentsOptions:
    ALLOW_COMMENTS = 1
    USER_CAN_VOTE_ON_COMMENTS = 2
    USER_CAN_SEE_RATINGS = 3

    CHOICES = [
        (ALLOW_COMMENTS, "Allow comments"),
        (USER_CAN_VOTE_ON_COMMENTS, "Users can vote on comments"),
        (USER_CAN_SEE_RATINGS, "Users can view ratings for this video"),
    ]
    
    
class Rating:
    POSITIVE = 1
    NEUTRAL = 0
    NEGATIVE = -1

    CHOICES = [
        (POSITIVE, "Positive"),
        (NEUTRAL, "Neutral"),
        (NEGATIVE, "Negative"),
    ]


class VideoStatus:
    UPLOADING = 1
    PROCESSING = 2
    ONLINE = 3
    FALIED = 4
    FALIED_TOO_LONG = 5
    SUSPENDED = 6
    SHADOWBANNED = 7

    CHOICES = [
        (UPLOADING, "Uploading"),
        (PROCESSING, "Processing"),
        (ONLINE, "Online"),
        (FALIED, "Falied"),
        (FALIED_TOO_LONG, "Falied (Too long)"),
        (SUSPENDED, "Suspended"),
        (SHADOWBANNED, "Shadowbanned")
    ]


class Status:
    OK = 1
    SUSPENDED = 2
    
class PlaylistType:
    WATCH_LATER = 0
    FAVORITES = 1
    LIKES = 2
    DISLIKES = 3
    HISTORY = 4
    CUSTOM = 5
    CHOICES = [
        (WATCH_LATER, "Watch Later"),
        (FAVORITES, "Favorites"),
        (LIKES, "Liked videos"),
        (DISLIKES, "Disliked videos"),
        (HISTORY, "History"),
        (CUSTOM, "Custom")
    ]
    
class PostAction:
    POSTED = 1 
    UPLOADED = 2
    CREATED_PLAYLIST = 3
    
    CHOICES = [
        (POSTED, "Posted"),
        (UPLOADED, "Uploaded"),
        (CREATED_PLAYLIST, "Created playlist"),
    ]
    
class VideoActions:
    ACTIONS = -1 
    DELETE = 1 
    
    CHOICES = [
        (ACTIONS, "Actions"),
        (DELETE, "Delete"),
    ]
    
class GuideTabs:
    INDEX: 1
    MY_PROFILE: 2
    SUBSCRIPTIONS: 3