import json
import os
import uuid

import streamlit as st
import requests
import time
from urllib.parse import quote

ttc_token_auth = os.getenv("TTC_BASIC_AUTH")
import re

ttc_token_url = os.getenv("TTC_TOKEN_URL", "https://id.stg.trimble-transportation.com/oauth2/token")
chat_url = os.getenv("TTC_CHAT_URL",
                     "https://cloud.stage.api.trimblecloud.com/transportation/core/v1/agents/multi/{agent_name}")
is_local = bool(os.getenv("IS_LOCAL", False))
access_token = "eyJraWQiOiJmYjgyNzZhYi1jMzU5LTQ1MDctYjIxNS00OWZhMzVhMjRkODQiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI1NjgxNzRjMy04MzFlLTRmZTAtODZjMi0yNzU5NTNlYzNjYmUiLCJ2ZXIiOiIxLjAiLCJyb2xlcyI6WyJUcmltYmxlIEFkbWluIl0sImlzcyI6Imh0dHBzOi8vaWQuZGV2LnRyaW1ibGUtdHJhbnNwb3J0YXRpb24uY29tIiwiYWNjb3VudF9pZCI6IjY2Mzc5ZDY4LTNmNjQtNDZiNi1iMzZkLTkxZDdiODBhY2UwYiIsIm5iZiI6MTY5NjMxODIwOSwicHJvZHVjdF9pZHMiOltdLCJoYXNfbW9yZV9yb2xlcyI6ZmFsc2UsImFjY291bnRfbmFtZSI6IlRyaW1ibGUgVHJhbnNwb3J0YXRpb24iLCJuYW1lIjoiTW90aGkgU2FtcGF0aCIsImlkZW50aXR5X3R5cGUiOiJ1c2VyIiwiZXhwIjoxNjk2MzIxODA5LCJpYXQiOjE2OTYzMTgyMDksImp0aSI6IjA3N2IxNDFmLWEyZjUtNDJkZi1iMjYwLTljZjk2OTcxZWU5MiIsImVtYWlsIjoibW90aGlfc2FtcGF0aEB0cmltYmxlLmNvbSJ9.CyRJrXIxduH7PHvs9ZFXZRFp-oZzEAJPel6WhJvsIi7XL-8Orm9rohLCvIoqGUoein_9DMIv1Eyg493FMrhaNHfFVVS3IIH3SpIa-h8eUHqzBp7GtP_u5XaswkVo4Z_DyNiQ1mW1F5IXvAMDX_N-vp2iOsqfJBoZ9WSP--LoPJMvx5Ra50RhiVBkuScdpE-D8TC7w5yL88BQvhOlMB-73c8dUpyKEFJfdj2QgQ4gq7FAH8mMP4PYtU7wqhOnDVuMB1jHx9MFWjtzLzneqiRkifx71OLNu7l3CPHVRPxe0SHVgKgh2S_K5gpMPJ-PtjizBV9Iy3QH4wxMrJMaJeTk5g"


def get_time():
    # ts stores the time in seconds
    return time.time()



def get_matches_carrier(match_type):
    # encoded_string = quote(carrier_id)
    carrier_id = st.session_state['carrier_uuid']
    search_url = "https://pzfightclub.dev.trimble-transportation.com/graph"
    # token = get_ttc_token()
    # print(token)
    payload = {
        "operationName": "getMatches",
        "variables": {
            "carrierUuid": carrier_id,
            "filter": "IGNORE_PAST_MATCHES"
        },
        "query": "query getMatches($carrierUuid: UUID!, $filter: MatchesQueryFilter) {\n  matches(carrierUuid: $carrierUuid, filter: $filter) {\n    uuid\n    proposalRequest {\n      uuid\n      trailerPoolRequirements\n      insuranceRequirements\n      laneNotes\n      placardsRequired\n      lumperAuthorized\n      temperatureProtectionRequired\n      matchClosingDate\n      anticipatedAwardDate\n      freightMovementBeginDate\n      freightMovementEndsDate\n      matchDraftId\n      modeOfTransportationType {\n        name\n        __typename\n      }\n      rateType {\n        uuid\n        name\n        __typename\n      }\n      weeklyMovements\n      lane {\n        uuid\n        trailerType {\n          uuid\n          name\n          __typename\n        }\n        shipper {\n          uuid\n          name\n          avatarUrl\n          __typename\n        }\n        destinationLocation {\n          address\n          name\n          place\n          postalCode\n          region\n          centerLngLat\n          accommodations {\n            uuid\n            name\n            __typename\n          }\n          __typename\n        }\n        originLocation {\n          address\n          name\n          place\n          postalCode\n          region\n          centerLngLat\n          timezoneName\n          accommodations {\n            uuid\n            name\n            __typename\n          }\n          __typename\n        }\n        stops {\n          centerLngLat\n          __typename\n        }\n        laneId\n        distance\n        distanceUom\n        pcmVersion\n        activeAgreementCount\n        openProposalRequestCount\n        __typename\n      }\n      currencyUom\n      loadingType {\n        uuid\n        name\n        __typename\n      }\n      unloadingType {\n        uuid\n        name\n        __typename\n      }\n      loadingBeginTime\n      loadingEndTime\n      unloadingBeginTime\n      unloadingEndTime\n      __typename\n    }\n    route {\n      uuid\n      name\n      __typename\n    }\n    score {\n      score\n      quality\n      __typename\n    }\n    status\n     agreements {\n      ...agreement\n      contract {\n        ...contract\n        __typename\n      }\n      __typename\n    }\n    needsAction\n    __typename\n  }\n}\n\nfragment proposalRequest on ProposalRequest {\n  uuid\n  matchDraftId\n  status\n  annualMovements\n  weeklyMovements\n  freightMovementBeginDate\n  freightMovementEndsDate\n  operationalizedAt\n  modeOfTransportationType {\n    ...modeOfTransportationType\n    __typename\n  }\n  lane {\n    uuid\n    owner {\n      uuid\n      firstName\n      lastName\n      email\n      phone\n      avatarUrl\n      __typename\n    }\n    trailerType {\n      uuid\n      name\n      __typename\n    }\n    shipper {\n      uuid\n      name\n      avatarUrl\n      __typename\n    }\n    destinationLocation {\n      ...shipperLocation\n      __typename\n    }\n    originLocation {\n      ...shipperLocation\n      __typename\n    }\n    stops {\n      ...shipperLocation\n      __typename\n    }\n    loadingType {\n      uuid\n      name\n      __typename\n    }\n    unloadingType {\n      uuid\n      name\n      __typename\n    }\n    laneId\n    distance\n    distanceUom\n    pcmVersion\n    activeAgreementCount\n    openProposalRequestCount\n    __typename\n  }\n  loadingBeginTime\n  loadingEndTime\n  unloadingBeginTime\n  unloadingEndTime\n  loadingPhone\n  unloadingPhone\n  loadingType {\n    uuid\n    name\n    __typename\n  }\n  unloadingType {\n    uuid\n    name\n    __typename\n  }\n  matchClosingDate\n  anticipatedAwardDate\n  rateType {\n    uuid\n    name\n    __typename\n  }\n  responses {\n    carrier {\n      name\n      uuid\n      __typename\n    }\n    __typename\n  }\n  insuranceRequirements\n  trailerPoolRequirements\n  laneNotes\n  activeAgreements {\n    uuid\n    acceptedAt\n    weeklyMovements\n    contractStatus\n    modeOfTransportationType {\n      ...modeOfTransportationType\n      __typename\n    }\n    __typename\n  }\n  placardsRequired\n  temperatureProtectionRequired\n  lumperAuthorized\n  distance\n  distanceUom\n  currencyUom\n  preassigned\n  allowAllAssetBrokers\n  __typename\n}\n\nfragment modeOfTransportationType on ModeOfTransportationType {\n  name\n  abbreviation\n  uuid\n  requiresTransitTime\n  __typename\n}\n\nfragment shipperLocation on ShipperLocation {\n  uuid\n  locationId\n  address\n  centerLngLat\n  name\n  place\n  postalCode\n  region\n  accommodations {\n    name\n    uuid\n    __typename\n  }\n  shipperLocationType {\n    name\n    uuid\n    __typename\n  }\n  loadingType {\n    uuid\n    name\n    __typename\n  }\n  loadingPhone\n  loadingBeginTime\n  loadingEndTime\n  allDayOperation\n  timezoneName\n  trimblePlaceId\n  shipperAddress\n  __typename\n}\n\nfragment proposalResponse on ProposalResponse {\n  uuid\n  acceptedAt\n  carrier {\n    uuid\n    name\n    fmcsaSafetyProfile {\n      entityType\n      __typename\n    }\n    __typename\n  }\n  maxWeeklyMovements\n  minWeeklyMovements\n  rate\n  rejectedAt\n  originRailroadRamp {\n    uuid\n    name\n    place\n    region\n    __typename\n  }\n  destinationRailroadRamp {\n    uuid\n    name\n    place\n    region\n    __typename\n  }\n  modeOfTransportationType {\n    ...modeOfTransportationType\n    __typename\n  }\n  transitTimeDurationDays\n  proposalRequest {\n    ...proposalRequest\n    __typename\n  }\n  scacUuid\n  distance\n  distanceUom\n  currencyUom\n  notes\n  type\n  __typename\n}\n\nfragment agreement on Agreement {\n  uuid\n  weeklyMovements\n  totalWeeklyMovements\n  allAmendments {\n    acceptedAt\n    acceptedWeeklyMovements\n    acceptedRate\n    confirmedAt\n    dueAt\n    amendmentEndsDate\n    amendmentStartsDate\n    proposedWeeklyMovements\n    status\n    rejectedAt\n    uuid\n    agreement {\n      uuid\n      proposalResponse {\n        ...proposalResponse\n        __typename\n      }\n      weeklyMovements\n      __typename\n    }\n    __typename\n  }\n  openAmendment {\n    acceptedAt\n    acceptedWeeklyMovements\n    acceptedRate\n    confirmedAt\n    dueAt\n    amendmentEndsDate\n    amendmentStartsDate\n    proposedWeeklyMovements\n    status\n    rejectedAt\n    uuid\n    agreement {\n      uuid\n      proposalResponse {\n        ...proposalResponse\n        __typename\n      }\n      weeklyMovements\n      __typename\n    }\n    __typename\n  }\n  contractStatus\n  status\n  notices {\n    ...notice\n    __typename\n  }\n  carrierMainContact {\n    uuid\n    firstName\n    lastName\n    avatarUrl\n    email\n    phone\n    __typename\n  }\n  proposalResponse {\n    ...proposalResponse\n    __typename\n  }\n  acceptedAt\n  rejectedAt\n  staleDate\n  reawardedAt\n  rejectionReason\n  canceledAt\n  freightMovementEndsDate\n  modeOfTransportationType {\n    ...modeOfTransportationType\n    __typename\n  }\n  __typename\n}\n\nfragment notice on Notice {\n  uuid\n  reason\n  acknowledgmentDueAt\n  acknowledgmentAt\n  agreement {\n    uuid\n    proposalResponse {\n      ...proposalResponse\n      __typename\n    }\n    weeklyMovements\n    __typename\n  }\n  shipperInitiated\n  __typename\n}\n\nfragment contract on Contract {\n  uuid\n  status\n  owners {\n    uuid\n    email\n    user {\n      uuid\n      email\n      __typename\n    }\n    organization {\n      ... on Carrier {\n        uuid\n        __typename\n      }\n      ... on Shipper {\n        uuid\n        __typename\n      }\n      __typename\n    }\n    magicLinks {\n      ... on MagicLinks {\n        token\n        expiresAt\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    final_payload = json.dumps(payload)
    response = requests.request("POST", search_url, headers=headers, data=final_payload)
    # print(response.text)
    data = json.loads(response.text)
    routes = data['data']
    # print(data)
    best_matches = []
    matches = []
    for record in routes['matches']:
        # Collect the required information
        lane = record['proposalRequest']['lane']
        origin_location = lane['originLocation']
        dest_location = lane['destinationLocation']
        origin_name = origin_location['place'] + "(" + origin_location['region']+")"
        dest_name = dest_location['place'] + "(" + dest_location['region']+")"
        status = record['status']
        shipper_name = lane['shipper']['name']
        trailer_type = lane['trailerType']['name']
        # name = record['name'] if 'name' in record else email
        # account_names = [account['name'] for account in record['accounts']]
        # Print the collected information
        # accounts = ', '.join(account_names)
        if record['score']['quality'] in ['EXCELLENT', 'HIGH']:
            best_matches.append(f"{origin_name} to {dest_name} of {trailer_type} by {shipper_name} of status {status}")
        matches.append(f"{origin_name} to {dest_name} of {trailer_type} by {shipper_name} of status {status}")
    if "best" in match_type and "without" not in match_type:
        return best_matches
    return matches


def get_best_matches_carrier():
    # encoded_string = quote(carrier_id)
    carrier_id = st.session_state['carrier_uuid']
    print(carrier_id)
    search_url = "https://pzfightclub.dev.trimble-transportation.com/graph"
    # token = get_ttc_token()
    # print(token)
    payload = {
        "operationName": "getMatches",
        "variables": {
            "carrierUuid": carrier_id,
            "filter": "IGNORE_PAST_MATCHES"
        },
        "query": "query getMatches($carrierUuid: UUID!, $filter: MatchesQueryFilter) {\n  matches(carrierUuid: $carrierUuid, filter: $filter) {\n    uuid\n    proposalRequest {\n      uuid\n      trailerPoolRequirements\n      insuranceRequirements\n      laneNotes\n      placardsRequired\n      lumperAuthorized\n      temperatureProtectionRequired\n      matchClosingDate\n      anticipatedAwardDate\n      freightMovementBeginDate\n      freightMovementEndsDate\n      matchDraftId\n      modeOfTransportationType {\n        name\n        __typename\n      }\n      rateType {\n        uuid\n        name\n        __typename\n      }\n      weeklyMovements\n      lane {\n        uuid\n        trailerType {\n          uuid\n          name\n          __typename\n        }\n        shipper {\n          uuid\n          name\n          avatarUrl\n          __typename\n        }\n        destinationLocation {\n          address\n          name\n          place\n          postalCode\n          region\n          centerLngLat\n          accommodations {\n            uuid\n            name\n            __typename\n          }\n          __typename\n        }\n        originLocation {\n          address\n          name\n          place\n          postalCode\n          region\n          centerLngLat\n          timezoneName\n          accommodations {\n            uuid\n            name\n            __typename\n          }\n          __typename\n        }\n        stops {\n          centerLngLat\n          __typename\n        }\n        laneId\n        distance\n        distanceUom\n        pcmVersion\n        activeAgreementCount\n        openProposalRequestCount\n        __typename\n      }\n      currencyUom\n      loadingType {\n        uuid\n        name\n        __typename\n      }\n      unloadingType {\n        uuid\n        name\n        __typename\n      }\n      loadingBeginTime\n      loadingEndTime\n      unloadingBeginTime\n      unloadingEndTime\n      __typename\n    }\n    route {\n      uuid\n      name\n      __typename\n    }\n    score {\n      score\n      quality\n      __typename\n    }\n    status\n     agreements {\n      ...agreement\n      contract {\n        ...contract\n        __typename\n      }\n      __typename\n    }\n    needsAction\n    __typename\n  }\n}\n\nfragment proposalRequest on ProposalRequest {\n  uuid\n  matchDraftId\n  status\n  annualMovements\n  weeklyMovements\n  freightMovementBeginDate\n  freightMovementEndsDate\n  operationalizedAt\n  modeOfTransportationType {\n    ...modeOfTransportationType\n    __typename\n  }\n  lane {\n    uuid\n    owner {\n      uuid\n      firstName\n      lastName\n      email\n      phone\n      avatarUrl\n      __typename\n    }\n    trailerType {\n      uuid\n      name\n      __typename\n    }\n    shipper {\n      uuid\n      name\n      avatarUrl\n      __typename\n    }\n    destinationLocation {\n      ...shipperLocation\n      __typename\n    }\n    originLocation {\n      ...shipperLocation\n      __typename\n    }\n    stops {\n      ...shipperLocation\n      __typename\n    }\n    loadingType {\n      uuid\n      name\n      __typename\n    }\n    unloadingType {\n      uuid\n      name\n      __typename\n    }\n    laneId\n    distance\n    distanceUom\n    pcmVersion\n    activeAgreementCount\n    openProposalRequestCount\n    __typename\n  }\n  loadingBeginTime\n  loadingEndTime\n  unloadingBeginTime\n  unloadingEndTime\n  loadingPhone\n  unloadingPhone\n  loadingType {\n    uuid\n    name\n    __typename\n  }\n  unloadingType {\n    uuid\n    name\n    __typename\n  }\n  matchClosingDate\n  anticipatedAwardDate\n  rateType {\n    uuid\n    name\n    __typename\n  }\n  responses {\n    carrier {\n      name\n      uuid\n      __typename\n    }\n    __typename\n  }\n  insuranceRequirements\n  trailerPoolRequirements\n  laneNotes\n  activeAgreements {\n    uuid\n    acceptedAt\n    weeklyMovements\n    contractStatus\n    modeOfTransportationType {\n      ...modeOfTransportationType\n      __typename\n    }\n    __typename\n  }\n  placardsRequired\n  temperatureProtectionRequired\n  lumperAuthorized\n  distance\n  distanceUom\n  currencyUom\n  preassigned\n  allowAllAssetBrokers\n  __typename\n}\n\nfragment modeOfTransportationType on ModeOfTransportationType {\n  name\n  abbreviation\n  uuid\n  requiresTransitTime\n  __typename\n}\n\nfragment shipperLocation on ShipperLocation {\n  uuid\n  locationId\n  address\n  centerLngLat\n  name\n  place\n  postalCode\n  region\n  accommodations {\n    name\n    uuid\n    __typename\n  }\n  shipperLocationType {\n    name\n    uuid\n    __typename\n  }\n  loadingType {\n    uuid\n    name\n    __typename\n  }\n  loadingPhone\n  loadingBeginTime\n  loadingEndTime\n  allDayOperation\n  timezoneName\n  trimblePlaceId\n  shipperAddress\n  __typename\n}\n\nfragment proposalResponse on ProposalResponse {\n  uuid\n  acceptedAt\n  carrier {\n    uuid\n    name\n    fmcsaSafetyProfile {\n      entityType\n      __typename\n    }\n    __typename\n  }\n  maxWeeklyMovements\n  minWeeklyMovements\n  rate\n  rejectedAt\n  originRailroadRamp {\n    uuid\n    name\n    place\n    region\n    __typename\n  }\n  destinationRailroadRamp {\n    uuid\n    name\n    place\n    region\n    __typename\n  }\n  modeOfTransportationType {\n    ...modeOfTransportationType\n    __typename\n  }\n  transitTimeDurationDays\n  proposalRequest {\n    ...proposalRequest\n    __typename\n  }\n  scacUuid\n  distance\n  distanceUom\n  currencyUom\n  notes\n  type\n  __typename\n}\n\nfragment agreement on Agreement {\n  uuid\n  weeklyMovements\n  totalWeeklyMovements\n  allAmendments {\n    acceptedAt\n    acceptedWeeklyMovements\n    acceptedRate\n    confirmedAt\n    dueAt\n    amendmentEndsDate\n    amendmentStartsDate\n    proposedWeeklyMovements\n    status\n    rejectedAt\n    uuid\n    agreement {\n      uuid\n      proposalResponse {\n        ...proposalResponse\n        __typename\n      }\n      weeklyMovements\n      __typename\n    }\n    __typename\n  }\n  openAmendment {\n    acceptedAt\n    acceptedWeeklyMovements\n    acceptedRate\n    confirmedAt\n    dueAt\n    amendmentEndsDate\n    amendmentStartsDate\n    proposedWeeklyMovements\n    status\n    rejectedAt\n    uuid\n    agreement {\n      uuid\n      proposalResponse {\n        ...proposalResponse\n        __typename\n      }\n      weeklyMovements\n      __typename\n    }\n    __typename\n  }\n  contractStatus\n  status\n  notices {\n    ...notice\n    __typename\n  }\n  carrierMainContact {\n    uuid\n    firstName\n    lastName\n    avatarUrl\n    email\n    phone\n    __typename\n  }\n  proposalResponse {\n    ...proposalResponse\n    __typename\n  }\n  acceptedAt\n  rejectedAt\n  staleDate\n  reawardedAt\n  rejectionReason\n  canceledAt\n  freightMovementEndsDate\n  modeOfTransportationType {\n    ...modeOfTransportationType\n    __typename\n  }\n  __typename\n}\n\nfragment notice on Notice {\n  uuid\n  reason\n  acknowledgmentDueAt\n  acknowledgmentAt\n  agreement {\n    uuid\n    proposalResponse {\n      ...proposalResponse\n      __typename\n    }\n    weeklyMovements\n    __typename\n  }\n  shipperInitiated\n  __typename\n}\n\nfragment contract on Contract {\n  uuid\n  status\n  owners {\n    uuid\n    email\n    user {\n      uuid\n      email\n      __typename\n    }\n    organization {\n      ... on Carrier {\n        uuid\n        __typename\n      }\n      ... on Shipper {\n        uuid\n        __typename\n      }\n      __typename\n    }\n    magicLinks {\n      ... on MagicLinks {\n        token\n        expiresAt\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    final_payload = json.dumps(payload)
    response = requests.request("POST", search_url, headers=headers, data=final_payload)
    # print(response.text)
    data = json.loads(response.text)
    routes = data['data']
    # print(data)
    return_text = []
    for record in routes['matches']:
        if record['score']['quality'] in ['EXCELLENT', 'BEST']:
            # Collect the required information
            lane = record['proposalRequest']['lane']
            origin_location = lane['originLocation']
            dest_location = lane['destinationLocation']
            origin_name = origin_location['name'] + " " + origin_location['place'] + " " + origin_location['region']
            dest_name = dest_location['name'] + " " + dest_location['place'] + " " + dest_location['region']
            status = record['status']
            shipper_name = lane['shipper']['name']
            trailer_type = lane['trailerType']['name']
            # name = record['name'] if 'name' in record else email
            # account_names = [account['name'] for account in record['accounts']]
            # Print the collected information
            # accounts = ', '.join(account_names)
            return_text.append(f"{origin_name} to {dest_name} of {trailer_type} by {shipper_name} of status '{status}' \n")

    return return_text


def get_tasks_carrier():
    # encoded_string = quote(carrier_id)
    carrier_id = st.session_state['carrier_uuid']
    search_url = "https://pzfightclub.dev.trimble-transportation.com/graph"
    # token = get_ttc_token()
    # print(token)
    payload = {
        "operationName": "tasks",
        "variables": {
            "organizationUuid": carrier_id,
            "organizationType": "CARRIER"
        },
        "query": "query tasks($organizationType: OrganizationType!, $organizationUuid: UUID!) {\n  tasks(organizationType: $organizationType, organizationUuid: $organizationUuid) {\n    ...task\n    __typename\n  }\n}\n\nfragment task on Task {\n  createdAt\n  dueAt\n  prompt\n  status\n  type\n  __typename\n}\n\n"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    final_payload = json.dumps(payload)
    response = requests.request("POST", search_url, headers=headers, data=final_payload)
    # print(response.text)
    data = json.loads(response.text)
    tasks = data['data']
    # print(data)
    return_text = []
    for record in tasks['tasks']:
        # Collect the required information
        message = record['prompt']
        status = record['status']
        message_type = record['type']
        return_text.append(f"{message} is {status} of type '{message_type}' \n")
    return return_text

