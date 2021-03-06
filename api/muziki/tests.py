import json
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .models import Songz
from .serializers import SongsSerializer

# Create your tests here.

# Test for our models
class SongsModelTest(APITestCase):
    def setUp(self):
        self.a_song = Songz.objects.create(
            title="Kwangwaru",
            artist="Gold Platnumz"
        )

    def test_song(self):
        """Test ensures that the song created in the setup exists"""
        self.assertEqual(self.a_song.title, "Kwangwaru")
        self.assertEqual(self.a_song.artist, "Gold Platnumz")
        self.assertEqual(str(self.a_song), "Kwangwaru - Gold Platnumz")

#test for our views
class BaseTestView(APITestCase):

    client = APIClient()

    def login_client(self, username="", password=""):
        #get a token from DRF
        response = self.client.post(
            reverse('create-token'),
            data=json.dumps(
                {
                    'username': username,
                    'password': password
                }
            ),
            content_type='application/json'
        )
        self.token = response.data['token']
        #set the token in the header
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer' + self.token
        )
        self.client.login(username=username, password=password)
        return self.token

    @staticmethod
    def create_song(title="", artist=""):
        if title != ""  and artist != "":
            Songz.objects.create(title=title, artist=artist)
    
    # def setUp(self):
    #     self.create_song("made a way", "travis greene")
    #     self.create_song("you waited", "travis greene")
    #     self.create_song("new position", "kansoul")

    def make_a_request(self, kind="post", **kwargs):
        """make a post request to create a song"""
        if kind == "post":
            return self.client.post(
                reverse(
                    "songs-list-create",
                    kwargs={
                        "version": kwargs["version"]
                    }
                ), 
                data=json.dumps(kwargs["data"]),
                content_type='application/json'
            )
        elif kind == "put":
            return self.client.put(
                reverse(
                    "songs-detail",
                    kwargs={
                        "version": kwargs["version"],
                        "pk": kwargs["id"]
                    }
                ),
                data=json.dumps(kwargs["data"]),
                content_type='application/json'
            )
        else:
            return None

    def fetch_a_song(self, pk=0):
        return self.client.get(
            reverse(
                "songs-detail",
                kwargs={
                    "version": "v1",
                    "pk": pk
                }
            )
        )

    def delete_a_song(self, pk=0):
        return self.client.delete(
            reverse(
                "songs-detail",
                kwargs={
                    "version": "v1",
                    "pk": pk
                }
            )
        )
    
    def login_a_user(self, username="", password=""):
        url = reverse(
            "auth-login",
            kwargs={
                "version": "v1"
            }
        )
        return self.client.post(
            url,
            data=json.dumps({
                "username": username,
                "password": password
            }),
            content_type='application/json'
        )

    def register_a_user(self, username="", password="", email=""):
        return self.client.post(
            reverse(
                "auth-register",
                kwargs={
                    "version": "v1"
                }
            ),
            data=json.dumps(
                {
                    "username": username,
                    "password": password,
                    "email": email
                }
            ),
            content_type='application/json'
        )


    def setUp(self):
        #create a admin user
        self.user = User.objects.create_superuser(
            username="test_user",
            email="test@mail.com",
            password="testing",
            first_name="test",
            last_name="user",
        )
        #add test data
        self.create_song("made a way", "travis greene")
        self.create_song("you waited", "travis greene")
        self.create_song("new position", "kansoul")


class AuthLoginUserTest(BaseTestView):
    """
    Tests for the auth/login endpoint
    """

    def test_login_user_with_valid_credentials(self):
        #test login with valid credentials
        response = self.login_a_user("test_user", "testing")
        #assert token key exists
        self.assertIn("token", response.data)
        #assert status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #test login with invalid credentials
        response = self.login_a_user("anonymous", "pass")
        #assert status code is 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
class GetAllSongsTest(BaseTestView):

    def test_get_all_songs(self):
        """Test ensures we get a list of all the songs added in our api"""
        self.login_client('test_user', 'testing')
        #hit the api endpoint
        response = self.client.get(
            reverse("songs-list-create", kwargs={"version":"v1"})
        )
        #fetch data from db
        expected = Songz.objects.all()
        serialized = SongsSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AuthRegisterUserTest(BaseTestView):

    
    """
    Tests for auth/register/ endpoint
    """
    def test_register_a_user_with_valid_data(self):
        url = reverse(
            "auth-register",
            kwargs={
                "version": "v1"
            }
        )
        response = self.client.post(
            url,
            data=json.dumps(
                {
                    "username": "new_user",
                    "password": "new_pass",
                    "email": "new_user@email.com"
                }
            ),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_register_a_user_with_invalid_data(self):
        url = reverse(
            "auth-register",
            kwargs={
                "version": "v1"
            }
        )
        response = self.client.post(
            url,
            data=json.dumps(
                {
                    "username": "",
                    "password": "",
                    "email": ""
                }
            ),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)