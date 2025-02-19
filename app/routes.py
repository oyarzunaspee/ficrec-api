from fastapi import APIRouter, HTTPException, status, Depends, Form
from models import User, Token, RecList, RecListConfig, Rec
from typing import List, Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import nh3

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

users_router = APIRouter(prefix="/users")
profile_router = APIRouter(prefix="/profile")
public_router = APIRouter(prefix="")


"""
FOR AUTH
"""

# POST NEW USER (REGISTER)

@users_router.post("/signup", description="Create new user")
async def create_user(username: str =  Form(...), password: str = Form(...)):
    username = nh3.clean(username)
    password = nh3.clean(password)
    user_exists = await User.find_by_username(username)
    if user_exists is None:
        try:
            new_user = User(
                username = username,
                password = User.hash_password(password)
            )
            await User.insert(new_user)
            return {"status": status.HTTP_201_CREATED}
        except Exception as e:
            return HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}")
    else:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error: Username already taken")


# POST FOR TOKEN (LOG IN)

@users_router.post("/login", description="Login for users")
async def login(user_form: OAuth2PasswordRequestForm = Depends()):
    user_exists = await User.find_by_username(nh3.clean(user_form.username))
    if user_exists is None:
        return HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong username or password")
    
    verify_password = user_exists.verify_password(nh3.clean(user_form.password))
    if verify_password is False:
        return HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong username or password")
    
    token = Token.create_access_token(user_exists)

    return Token(access_token=token)


"""
AUTH
"""

# GET USER COLLECTIONS

@profile_router.get("/collections", response_model=List[RecList], description="List user's collections")
async def get_user_reclists(token: Token = Depends(oauth2_scheme)):
    current_user_id = Token(access_token=token).get_current_user()
    reclists = await RecList.find(RecList.user_id == current_user_id).to_list()
    return reclists


# POST NEW COLLECTION

@profile_router.post("/collections/new", description="Create collection")
async def create_reclist(
        name: Annotated[str, Form()],
        token: Token = Depends(oauth2_scheme)
    ):
    try:
        current_user_id = Token(access_token=token).get_current_user()
        new_reclist = RecList(name=nh3.clean(name), user_id=current_user_id, config=RecListConfig())
        await RecList.insert(new_reclist)
        return {"status": status.HTTP_201_CREATED}
    except Exception as e:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")


# PUT COLLECTION
@profile_router.put(
        "/collections/{reclist_id}",
        description = "Edit collection",
    )
async def edit_reclist(
        reclist_id: str,
        reclist_form: RecList,
        token: Token = Depends(oauth2_scheme)
    ):
    try:
        reclist = await RecList.get(reclist_id)
        if not Token.authorize_user(token, reclist.user_id):
            return {"status": status.HTTP_401_UNAUTHORIZED}
        
        if reclist_form.name is not None:
            reclist.name = nh3.clean(reclist_form.name)
        if reclist_form.about is not None:
            reclist.about = nh3.clean(reclist_form.about)
        await reclist.replace()
        return {"status": status.HTTP_200_OK}
    except Exception as e:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")


# PRIVATE / UNPRIVATE COLLECTION

@profile_router.put(
        "/collections/{reclist_id}/private",
        description = "Edit collection privacy",
    )
async def edit_reclist_privacy(
        reclist_id: str,
        privacy: Annotated[bool, Form()],
        token: Token = Depends(oauth2_scheme)
    ):
    try:
        reclist = await RecList.get(reclist_id)
        if not Token.authorize_user(token, reclist.user_id):
            return {"status": status.HTTP_401_UNAUTHORIZED}
        
        reclist.private = privacy
        await reclist.replace()
        return {"status": status.HTTP_200_OK}
    except Exception as e:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")


# UPDATE COLLECTION CONFIG
@profile_router.put("/collections/{reclist_id}/config")
async def update_reclist_config(reclist_id: str, config_form: RecListConfig, token: Token = Depends(oauth2_scheme)):
    try:
        config = RecListConfig(**config_form.model_dump())
        reclist = await RecList.get(reclist_id)
        if not Token.authorize_user(token, reclist.user_id):
            return {"status": status.HTTP_401_UNAUTHORIZED}
        reclist.config = config
        await reclist.replace()
        return {"status": status.HTTP_200_OK}
    except Exception as e:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")


# DELETE COLLECTION

@profile_router.delete("/collections/{reclist_id}/delete")
async def delete_reclist(reclist_id: str, token: Token = Depends(oauth2_scheme)):
    try:
        reclist = await RecList.get(reclist_id)
        if not Token.authorize_user(token, reclist.user_id):
            return {"status": status.HTTP_401_UNAUTHORIZED}
        
        reclist.deleted = True
        await reclist.replace()
        return {"status": status.HTTP_200_OK}
    except Exception as e:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")


# POST NEW REC

@profile_router.post("/collections/{reclist_id}/recs/new")
async def add_rec(reclist_id: str, rec_form: Rec, token: Token = Depends(oauth2_scheme)):
    reclist = await RecList.get(reclist_id)
    if not Token.authorize_user(token, reclist.user_id):
            return {"status": status.HTTP_401_UNAUTHORIZED}
    try:
        await Rec.insert(rec_form)
        return {"status": status.HTTP_200_OK}
    except Exception as e:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")


# GET COLLECTION RECS

@profile_router.get("/collections/{reclist_id}/recs", response_model=List[Rec])
async def get_reclist_recs(reclist_id: str, token: Token = Depends(oauth2_scheme)):
    current_user_id = Token(access_token=token).get_current_user()
    recs = await Rec.find(Rec.user_id == current_user_id, Rec.reclist_id == reclist_id, Rec.deleted == False).to_list()
    return recs


# DELETE REC
@profile_router.delete("/collections/{reclist_id}/recs/{rec_id}/delete")
async def delete_rec(reclist_id: str, rec_id: str, token: Token = Depends(oauth2_scheme)):
    try:
        rec = await Rec.get(rec_id)
        if not Token.authorize_user(token, rec.user_id):
            return {"status": status.HTTP_401_UNAUTHORIZED}
        rec.deleted = True
        rec.replace()
        return {"status": status.HTTP_200_OK}
    except Exception as e:
        return HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"Error: {e}")

"""
NO AUTH
"""

# GET USER COLLECTIONS
@public_router.get("/{username}/collections", response_model=List[RecList])
async def get_public_reclists(username: str):
    user = await User.find_one(User.username == username, User.is_active == True)
    reclists = await RecList.find(RecList.user_id == str(user.id), RecList.private == False, RecList.deleted == False).to_list()
    return reclists


# GET USER COLLECTION RECS
@public_router.get("/{username}/collections/{reclist_id}", response_model=List[Rec])
async def get_public_reclist_recs(username: str, reclist_id: str):
    recs = await Rec.find(Rec.reclist_id == reclist_id, Rec.deleted == False).to_list()
    return recs