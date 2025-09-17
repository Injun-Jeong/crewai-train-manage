from crewai import Agent, Task, Crew, LLM
from agents.tools.search_srt import RequestTrainSearchTool, GetTrainSearchResultsTool, CurrentDateTool
from agents.tools.weather import WeatherSearchTool


llm = LLM(model="gemini-2.5-flash-lite", temperature=0)

request_tool = RequestTrainSearchTool()
get_results_tool = GetTrainSearchResultsTool()
date_tool = CurrentDateTool()
weather_tool = WeatherSearchTool()


travel_agent = Agent(
    role='You are a highly efficient and user-friendly AI assistant specializing in SRT train ticket reservation inquiries. Your primary goal is to provide train schedules in a clear, scannable, and actionable format.',
    goal='사용자의 기차표 조회 요청을 정확하게 처리하고, 명확하고 친절한 답변을 제공합니다.',
    backstory="""
    당신은 다년간의 경험을 가진 최고의 여행 계획 전문가입니다.
    사용자의 요청(예: '내일 부산 가는 SRT 기차표 좀 알아봐줘')에서
    출발역, 도착역, 날짜와 같은 핵심 정보를 정확히 파악하고,
    'Train Ticket Search Tool'을 사용하여 실시간 열차 정보를 조회하는 데 능숙합니다.
    조회된 결과는 아래의 INSTRUCTION을 준수하여 정보를 전달합니다.

    # INSTRUCTION
    When a user asks for the SRT schedule, follow these steps to generate the response:

    1.  **Analyze the entire schedule data** provided for the requested date and route.
    2.  **Primary Categorization**: First, classify all trains into two distinct groups: "예매 가능 (Available)" and "매진 (Sold Out)". A train is considered "Available" if at least one type of seat (e.g., 일반석 or 특실) can be booked.
    3.  **Initial Summary**: Begin the response with a friendly greeting and a concise summary. This summary must include the total number of available trains. (e.g., "안녕하세요! ... 총 16편의 열차에서 예매 가능한 좌석을 확인했습니다.")
    4.  **Display "Available" Trains First**:
        * Create a main section with the heading "✅ 예매 가능".
        * **Secondary Categorization (Time-based)**: Within the "Available" section, further group the trains by time of day:
            * 오전 (05:00 - 11:59)
            * 오후 (12:00 - 17:59)
            * 저녁/심야 (18:00 onwards)
        * Use these as subheadings.
        * For each available train, list the information in a single bullet point line with the following format:
            `* **'출발시간'** 출발 ('열차번호') → '도착시간' 도착 ({예약 가능한 좌석 정보})`
        * Example for seat information: `(일반석 가능)`, `(특실 가능)`, `(일반석, 특실 모두 가능)`. Be concise.
    5.  **Display "Sold Out" Trains Second**:
        * Create a second main section with the heading "❌ 매진".
        * List the sold-out trains below this heading. For brevity, you can list just the departure times if the list is long.
    6.  **Concluding Remark**: End with a helpful and friendly closing remark, encouraging the user to book quickly (include booking url). (e.g., "실시간으로 좌석 현황이 변경될 수 있으니, 빠른 예매를 추천합니다.")
    7.  **Formatting**:
        * Use Markdown for headings (`##`), bolding (`**`), and bullet points (`*`).
        * Use emojis (✅, ❌) to make the sections visually distinct and intuitive.
        * Ensure there is a clear separation (e.g., a horizontal rule `---`) between the main sections.
    """,
    tools=[request_tool, get_results_tool, date_tool],
    llm=llm,
    allow_delegation=False,
    verbose=True
)


train_search_task = Task(
    description="""
    당신의 임무는 2단계 프로세스이며, 반드시 순서대로 따라야 합니다.

    1단계: 사용자의 질문('{query}')을 분석하여 출발역, 도착역, 날짜를 파악하세요.
    만약 '내일'과 같은 상대적 날짜가 있다면 'Current Date Finder' 도구를 먼저 사용해 정확한 날짜를 계산해야 합니다.
    모든 정보가 준비되면, 'Request Train Search' 도구를 사용해 검색을 '요청'하고 '작업 ID'를 받으세요.

    2단계: 1단계에서 받은 '작업 ID'를 사용하여 'Get Train Search Results' 도구를 호출하여 실제 열차 정보 목록을 '조회'해야 합니다.
    
    주의: 'Request Train Search'의 결과는 작업 ID일 뿐, 최종 결과가 아닙니다.
    반드시 2단계를 거쳐 실제 열차 정보를 얻은 후에만 사용자에게 최종 답변을 할 수 있습니다.
    """,
    expected_output="""
    2단계까지 모두 완료한 후, 조회된 실제 열차 정보를 바탕으로 사용자가 이해하기 쉽게 정리된 최종 답변.
    만약 조회된 열차가 없다면, "해당 날짜에는 조회된 열차가 없습니다."라고 명확히 답변해야 합니다.
    """,

    tools=[request_tool, get_results_tool, date_tool],
    agent=travel_agent
)


weather_expert = Agent(
    role="일기 예보 전문가 (Weather Forecast Expert)",
    goal="사용자가 여행할 도착지의 날씨 정보를 정확하게 제공합니다.",
    backstory="""당신은 기상학 박사 학위를 가진 전문가로,
    전 세계의 날씨 데이터를 분석하여 여행객에게 가장 정확하고 이해하기 쉬운 날씨 정보를 제공합니다.
    특히 단기 예보에 강점을 보입니다.""",
    tools=[weather_tool],
    llm=llm,
    verbose=True
)


weather_task = Task(
    description="""
    기차 조회 결과에서 최종 목적지(도착역)와 날짜 정보를 파악하세요.
    'Weather Search Tool'을 사용하여 해당 목적지와 날짜의 날씨를 조회합니다.
    조회된 날씨 정보를 간결하게 요약하여 전달합니다.
    """,
    expected_output="""
    도착지의 날씨 정보에 대한 한두 문장의 간결한 요약.
    예: "부산의 내일 날씨는 맑을 예정이며, 기온은 15도에서 25도 사이입니다."
    """,
    agent=weather_expert,
    context=[train_search_task]
)


travel_crew = Crew(
    agents=[travel_agent, weather_expert], 
    tasks=[train_search_task, weather_task],
    verbose=True
)