from typing import List
from uuid import UUID

import sqlalchemy as sa
from fastapi import Body, Depends, HTTPException, Path

from prefect.orion import models, schemas
from prefect.orion.api import dependencies
from prefect.orion.utilities.server import OrionRouter

router = OrionRouter(prefix="/flow_run_states", tags=["Flow Run States"])


@router.post("/")
async def create_flow_run_state(
    flow_run_id: UUID = Body(...),
    state: schemas.actions.StateCreate = Body(...),
    session: sa.orm.Session = Depends(dependencies.get_session),
) -> schemas.states.State:
    """
    Create a flow run state, invoking orchestration logic
    """
    return (
        await models.flow_run_states.orchestrate_flow_run_state(
            session=session,
            # convert to a full State object
            state=schemas.states.State.parse_obj(state),
            flow_run_id=flow_run_id,
            apply_orchestration_rules=False,
        )
    ).state


@router.get("/{id}")
async def read_flow_run_state(
    flow_run_state_id: UUID = Path(
        ..., description="The flow run state id", alias="id"
    ),
    session: sa.orm.Session = Depends(dependencies.get_session),
) -> schemas.states.State:
    """
    Get a flow run state by id
    """
    flow_run_state = await models.flow_run_states.read_flow_run_state(
        session=session, flow_run_state_id=flow_run_state_id
    )
    if not flow_run_state:
        raise HTTPException(status_code=404, detail="Flow run state not found")
    return flow_run_state


@router.get("/")
async def read_flow_run_states(
    flow_run_id: UUID,
    session: sa.orm.Session = Depends(dependencies.get_session),
) -> List[schemas.states.State]:
    """
    Get states associated with a flow run
    """
    return await models.flow_run_states.read_flow_run_states(
        session=session, flow_run_id=flow_run_id
    )
