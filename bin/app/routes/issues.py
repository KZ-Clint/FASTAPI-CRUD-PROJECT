import uuid
from fastapi import APIRouter, HTTPException, status
from app.schemas import IssueCreate, IssueUpdate, IssueOut, IssueStatus
from app.storage import load_data, save_data

router = APIRouter( prefix="/api/v1/issues", tags=["issues"] )

@router.get("/", response_model=list[IssueOut])
async def get_issues():
    issues = load_data()
    return issues

@router.post("/", response_model=IssueOut, status_code=status.HTTP_201_CREATED)
def create_issue(payload:IssueCreate):
    issues = load_data()
    new_issue = {  
        "id" : str(uuid.uuid4()),
        "title" : payload.title,
        "description" : payload.description,
        "priority" : payload.priority,
        "status" : IssueStatus.open
    }
    issues.append(new_issue)
    print(issues)
    save_data(issues)
    return new_issue

@router.get("/{issue_id}", response_model=IssueOut)
def get_specific_issues(issue_id:str):
    f_returned_issue = None

    issues = load_data()
    returned_issue = [ issue for issue in issues if issue["id"] == issue_id ]

    print(returned_issue)

    if len(returned_issue) > 0:
        f_returned_issue = returned_issue[0]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")


    return f_returned_issue

@router.put("/{id}", response_model=IssueOut, status_code=status.HTTP_200_OK )
def update_issue(id:str, payload:IssueUpdate):
    issues = load_data()
    update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
    updated_issue = None

    def map_issues(issue):
        nonlocal updated_issue
        if issue["id"] == id:
            new_issue = { **issue, **update_data }
            updated_issue = new_issue
            return new_issue
        return issue
            
    new_issues = [ map_issues(issue) for issue in issues ]
    print(new_issues)

    if updated_issue:
        save_data(new_issues)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue to be modified not found")

    return updated_issue


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(id:str):
    issues = load_data()

    new_issues = [ issue for issue in issues if issue["id"] != id ]
    print(new_issues)
    if len(new_issues) == len(issues):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
   
    save_data(new_issues)

    
    
  