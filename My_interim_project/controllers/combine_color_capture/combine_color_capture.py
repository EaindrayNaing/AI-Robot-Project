from controller import Robot

# ================= CONSTANTS =================
MAX_SPEED = 6.28
MULTIPLIER = 0.5
OBSTACLE_DISTANCE = 0.02

MIN_INTENSITY = 60

# Dog RGB (reference)
DOG_R = 77
DOG_G = 80
DOG_B = 89
TOLERANCE = 40

DOG_CONFIRMATION = 5

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

mode = "color"

image_counter = 0
captured = False
dog_detect_count = 0

# ================= FUNCTIONS =================
def front_obstacle():
    left = distance_sensors[0].getValue() / 4096.0
    right = distance_sensors[7].getValue() / 4096.0
    return (left + right) / 2 > OBSTACLE_DISTANCE


def get_center_rgb():
    width = camera.getWidth()
    height = camera.getHeight()
    image = camera.getImage()

    x = width // 2
    y = height // 2

    r = camera.imageGetRed(image, width, x, y)
    g = camera.imageGetGreen(image, width, x, y)
    b = camera.imageGetBlue(image, width, x, y)

    return r, g, b


def is_dog(r, g, b):
    return (abs(r - DOG_R) < TOLERANCE and
            abs(g - DOG_G) < TOLERANCE and
            abs(b - DOG_B) < TOLERANCE)


def capture_image(image_id):
    filename = f"dog_capture_{image_id}.png"
    camera.saveImage(filename, 100)
    print("Image saved:", filename)


def print_summary():
    colours = []
    if red_seen:
        colours.append("red")
    if green_seen:
        colours.append("green")
    if blue_seen:
        colours.append("blue")

    if len(colours) == 2:
        print("I see " + colours[0] + " and " + colours[1])
    elif len(colours) == 3:
        print("I see " + colours[0] + ", " + colours[1] + " and " + colours[2])


# ================= MAIN LOOP =================
while robot.step(timestep) != -1:

    # ===== GET RGB =====
    r, g, b = get_center_rgb()

    # ===== MODE 1: COLOR DETECTION =====
    if mode == "color":

        # Movement always active
        if front_obstacle():
            left_motor.setVelocity(-MAX_SPEED * MULTIPLIER)
            right_motor.setVelocity(MAX_SPEED * MULTIPLIER)
        else:
            left_motor.setVelocity(MAX_SPEED * MULTIPLIER)
            right_motor.setVelocity(MAX_SPEED * MULTIPLIER)

        if r > MIN_INTENSITY and r > g and r > b and not red_seen:
            print("I see red")
            red_seen = True
            print_summary()

        elif g > MIN_INTENSITY and g > r and g > b and not green_seen:
            print("I see green")
            green_seen = True
            print_summary()

        elif b > MIN_INTENSITY and b > r and b > g and not blue_seen:
            print("I see blue")
            blue_seen = True
            print_summary()

        if red_seen and green_seen and blue_seen:
            print("All colors detected. Start searching for dog...")
            mode = "dog"

    # ===== MODE 2: DOG DETECTION =====
    elif mode == "dog":

        if is_dog(r, g, b):
            dog_detect_count += 1
        else:
            dog_detect_count = 0
            captured = False  # allow new capture later

        if dog_detect_count >= DOG_CONFIRMATION:
            print("DOG DETECTED")

            # Stop ONLY when dog is visible
            left_motor.setVelocity(0)
            right_motor.setVelocity(0)

            if not captured:
                capture_image(image_counter)
                image_counter += 1
                captured = True

        else:
            # No dog → keep moving
            if front_obstacle():
                left_motor.setVelocity(-MAX_SPEED * MULTIPLIER)
                right_motor.setVelocity(MAX_SPEED * MULTIPLIER)
            else:
                left_motor.setVelocity(MAX_SPEED * MULTIPLIER)
                right_motor.setVelocity(MAX_SPEED * MULTIPLIER)