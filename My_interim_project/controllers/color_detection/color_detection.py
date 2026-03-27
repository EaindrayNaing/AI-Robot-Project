from controller import Robot

# ================= CONSTANTS =================
MAX_SPEED = 6.28
MULTIPLIER = 0.5
OBSTACLE_DISTANCE = 0.02

DOMINANCE_MARGIN = 25
MIN_INTENSITY = 60

# ================= ROBOT SETUP =================
robot = Robot()
timestep = int(robot.getBasicTimeStep())

sensor_names = ["ps0","ps1","ps2","ps3","ps4","ps5","ps6","ps7"]
distance_sensors = []

for name in sensor_names:
    sensor = robot.getDevice(name)
    sensor.enable(timestep)
    distance_sensors.append(sensor)

camera = robot.getDevice("camera")
camera.enable(timestep)

left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")

left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

left_motor.setVelocity(0)
right_motor.setVelocity(0)

# ================= MEMORY =================
red_seen = False
blue_seen = False
green_seen = False

# ================= FUNCTIONS =================
def front_obstacle():
    left = distance_sensors[0].getValue() / 4096.0
    right = distance_sensors[7].getValue() / 4096.0
    return (left + right) / 2 > OBSTACLE_DISTANCE


def print_summary():
    colours = []

    if blue_seen:
        colours.append("blue")
    if green_seen:
        colours.append("green")
    if red_seen:
        colours.append("red")

    if len(colours) == 2:
        print("I see " + colours[0] + " and " + colours[1])

    elif len(colours) == 3:
        print("I see " + colours[0] + ", " + colours[1] + " and " + colours[2])


# ================= MAIN LOOP =================
while robot.step(timestep) != -1:

    # ===== OBSTACLE AVOIDANCE =====
    if front_obstacle():
        left_motor.setVelocity(-MAX_SPEED * MULTIPLIER)
        right_motor.setVelocity(MAX_SPEED * MULTIPLIER)
    else:
        left_motor.setVelocity(MAX_SPEED * MULTIPLIER)
        right_motor.setVelocity(MAX_SPEED * MULTIPLIER)

    # ===== STOP DETECTION AFTER ALL COLOURS =====
    if red_seen and blue_seen and green_seen:
        continue

    # ===== CAMERA DATA =====
    width = camera.getWidth()
    height = camera.getHeight()
    image = camera.getImage()

    x = width // 2
    y = height // 2

    r = camera.imageGetRed(image, width, x, y)
    g = camera.imageGetGreen(image, width, x, y)
    b = camera.imageGetBlue(image, width, x, y)

    # ===== RED DETECTION =====
    if r > MIN_INTENSITY and r - max(g,b) > DOMINANCE_MARGIN and not red_seen:
        print("I see red")
        red_seen = True
        print_summary()

    # ===== BLUE DETECTION =====
    elif b > MIN_INTENSITY and b - max(r,g) > DOMINANCE_MARGIN and not blue_seen:
        print("I see blue")
        blue_seen = True
        print_summary()

    # ===== GREEN DETECTION =====
    elif g > MIN_INTENSITY and g - max(r,b) > DOMINANCE_MARGIN and not green_seen:
        print("I see green")
        green_seen = True
        print_summary()