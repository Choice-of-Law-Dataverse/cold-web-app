from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api/submarine", tags=["Submarine"])


@router.get("/", response_class=HTMLResponse)
def submarine():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deep Sea Submarine</title>
    <style>
        /* Deep sea background */
        body {
        margin: 0;
        padding: 0;
        background: linear-gradient(to bottom, #003366, #000022);
        overflow: hidden;
        height: 100vh;
        position: relative;
        }
        /* Submarine container: animated horizontally (left) and vertically (translateY) */
        .submarine {
        position: absolute;
        width: 150px;
        height: 70px;
        /* Two animations:
            - moveSubmarine: controls horizontal (left) movement
            - floatSubmarine: adds a gentle vertical floating effect via translateY */
        animation: moveSubmarine 10s linear infinite, floatSubmarine 5s ease-in-out infinite;
        }
        /* Main body of the submarine */
        .submarine .body {
        position: absolute;
        width: 100%;
        height: 100%;
        background: yellow;
        border-radius: 35px 35px 20px 20px;
        border: 3px solid #666;
        box-shadow: inset 5px 0 0 rgba(0,0,0,0.2);
        }
        /* Decorative stripe on the submarine */
        .submarine .stripe {
        position: absolute;
        width: 12px;
        height: 70%;
        background: #f5c542;
        top: 15%;
        left: 40%;
        border-radius: 6px;
        }
        /* Periscope */
        .submarine .periscope {
        position: absolute;
        width: 12px;
        height: 30px;
        background: #555;
        top: -30px;
        left: 50%;
        transform: translateX(-50%);
        border-radius: 5px;
        }
        /* Horizontal extension for the periscope */
        .submarine .periscope::after {
        content: "";
        position: absolute;
        top: 0;
        left: -5px;
        width: 22px;
        height: 8px;
        background: #555;
        border-radius: 3px;
        }
        /* Window on the submarine */
        .submarine .window {
        position: absolute;
        top: 20px;
        left: 25px;
        width: 30px;
        height: 30px;
        background: #fff;
        border-radius: 50%;
        border: 2px solid #333;
        }
        /* Propeller */
        .submarine .propeller {
        position: absolute;
        width: 20px;
        height: 20px;
        background: #333;
        bottom: 5px;
        left: -15px;
        border-radius: 50%;
        animation: spinPropeller 1s linear infinite;
        }
        @keyframes spinPropeller {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
        }
        /* Horizontal movement: the submarine sails from left to right and then back */
        @keyframes moveSubmarine {
        0% { left: -200px; }
        50% { left: calc(100% - 150px); }
        100% { left: -200px; }
        }
        /* Vertical floating: the submarine gently moves up and down */
        @keyframes floatSubmarine {
        50%, 100% { transform: translateY(100); }
        50% { transform: translateY(250px); }
        }
        /* Bubbles rising in the deep sea */
        .bubble {
        position: absolute;
        background-color: rgba(255, 255, 255, 0.7);
        border-radius: 50%;
        opacity: 0.7;
        animation: bubbleRise 5s linear infinite;
        }
        @keyframes bubbleRise {
        0% { transform: translateY(0) scale(0.5); opacity: 1; }
        100% { transform: translateY(-200px) scale(1); opacity: 0; }
        }
    </style>
    </head>
    <body>
    <div class="submarine">
        <div class="body"></div>
        <div class="stripe"></div>
        <div class="periscope"></div>
        <div class="window"></div>
        <div class="propeller"></div>
    </div>
    <!-- JavaScript to create rising bubbles -->
    <script>
        function createBubble() {
        const bubble = document.createElement('div');
        bubble.classList.add('bubble');
        const size = Math.random() * 20 + 10; // random size between 10px and 30px
        bubble.style.width = size + 'px';
        bubble.style.height = size + 'px';
        bubble.style.left = Math.random() * window.innerWidth + 'px';
        bubble.style.bottom = '0px';
        // Randomize the duration for a natural effect
        bubble.style.animationDuration = (Math.random() * 3 + 2) + 's';
        document.body.appendChild(bubble);
        // Remove the bubble after its animation completes
        setTimeout(() => bubble.remove(), parseFloat(bubble.style.animationDuration) * 1000);
        }
        // Create a bubble every 500 milliseconds
        setInterval(createBubble, 500);
    </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
