"""Campaign Endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user_id
from app.crud import crud_campaign
from app.schemas.campaign import CampaignCreate, CampaignResponse

router = APIRouter()

@router.get("/", response_model=list[CampaignResponse])
def read_campaigns(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud_campaign.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=CampaignResponse)
def create_campaign(campaign_in: CampaignCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return crud_campaign.create(db, obj_in=campaign_in, user_id=current_user_id) 