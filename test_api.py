import requests
import json

GRAPHQL_URL = "https://api.studiegids.uva.nl/graphql"

# Try the exact same query the browser sends
QUERY = """query getProgrammePageById($academicYear: Int!, $id: Int!, $language: CourseCatalogLanguage!) {
  programmePageById(academicYear: $academicYear, id: $id, language: $language) {
    id
    name
    parentPageId
    index
    hasContent
    isBilingual
    content
    curriculum {
      id
      instructionLanguages
      studyPaths {
        id
        type
        name
        description
        __typename
      }
      years {
        id
        description
        year
        credits
        nodes {
          ...curriculumNodes
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}

fragment curriculumNodes on CurriculumPreviewNode {
  id
  minCredits
  maxCredits
  name
  ... on CurriculumGroup {
    ...curriculumGroup
    __typename
  }
  ... on CurriculumGrouping {
    ...curriculumGrouping
    nodes {
      ... on CurriculumGroup {
        ...curriculumGroup
        __typename
      }
      __typename
    }
    __typename
  }
  ... on CurriculumStudyPathGroup {
    studyPathId
    nodes {
      ... on CurriculumGroup {
        ...curriculumGroup
        __typename
      }
      ... on CurriculumGrouping {
        ...curriculumGrouping
        nodes {
          ... on CurriculumGroup {
            ...curriculumGroup
            __typename
          }
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
  __typename
}

fragment courses on CurriculumCourse {
  id
  code
  name
  credits
  offerings {
    id
    periods
    __typename
  }
  __typename
}

fragment curriculumGroup on CurriculumGroup {
  id
  minCredits
  maxCredits
  name
  type
  description
  periods
  courses {
    ...courses
    __typename
  }
  __typename
}

fragment curriculumGrouping on CurriculumGrouping {
  id
  minCredits
  maxCredits
  name
  __typename
}"""

response = requests.post(
    GRAPHQL_URL,
    json={
        "operationName": "getProgrammePageById",
        "variables": {"id": 36812, "academicYear": 2025, "language": "ENGLISH"},
        "extensions": {"clientLibrary": {"name": "@apollo/client", "version": "4.1.9"}},
        "query": QUERY
    },
    headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://coursecatalogue.uva.nl",
        "Referer": "https://coursecatalogue.uva.nl/"
    }
)

data = response.json()
print(json.dumps(data, indent=2)[:5000])