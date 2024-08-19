import pygame
from pygame.math import Vector2
from pygame import Color
import math
from physics import Disk, Bullet
from camera import Camera


# TODO: Move constant somewhere else
BULLET_SPEED = 500
GUNBARREL_LENGTH = 3  # relative to radius
GUNBARREL_WIDTH = 0.5  # relative to radius


class Ship(Disk):
    def __init__(
        self, pos: Vector2, vel: Vector2, density: float, size: float, color: Color
    ):
        super().__init__(pos, vel, density, size, color)
        self.size = size
        self.angle = 0
        self.health = 10000.0
        self.REPAIR_RATE = 0.1
        self.REFUEL_RATE = 0.2
        self.MAX_health = 200.0
        self.bullets: list[Bullet] = []
        self.gun_cooldown = 3

        self.ammo = 250
        self.thrust = 50 * self.mass
        self.rotation_thrust = 100
        self.thruster_rot_left = False
        self.thruster_rot_right = False
        self.thruster_backward = False
        self.thruster_forward = False
        self.fuel = 100.0
        self.fuel_consumption_rate = 0.07
        self.rotation_fuel_consumption_rate = 0.03
        self.MAX_FUEL = 100.0

    def get_faced_direction(self):
        # TODO: Why doesn't Vector2.from_polar() work?
        return Vector2(
            math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))
        )

    def shoot(self):
        if self.gun_cooldown <= 0 and self.ammo > 0:
            forward = self.get_faced_direction()
            bullet_pos = self.pos + forward * self.radius * GUNBARREL_LENGTH
            bullet_vel = self.vel + forward * BULLET_SPEED
            self.bullets.append(Bullet(bullet_pos, bullet_vel, pygame.Color("blue")))
            self.gun_cooldown = 0.25
            self.ammo -= 1

    def step(self, dt: float):
        if self.thruster_rot_left:
            self.angle += self.rotation_thrust * dt
        if self.thruster_rot_right:
            self.angle -= self.rotation_thrust * dt

        forward = self.get_faced_direction()
        if self.thruster_forward:
            self.apply_force(forward * self.thrust, dt)
        if self.thruster_backward:
            self.apply_force(-forward * self.thrust, dt)

        super().step(dt)

        self.gun_cooldown = max(0, self.gun_cooldown - dt)

        # TODO: This is unnecessary, move to only the fuel-modification places.
        self.fuel = max(0, self.fuel)

    def draw(self, camera: Camera):
        forward = self.get_faced_direction()
        right = pygame.math.Vector2(-forward.y, forward.x)
        left = -right
        backward = -forward

        darker_color = Color(self.color)
        darker_color.r = darker_color.r // 2
        darker_color.g = darker_color.g // 2
        darker_color.b = darker_color.b // 2
        ship_screen_pos = camera.world_to_camera(self.pos)

        # TODO: Especially the backward-thruster is super ugly
        # thruster_backward (active)
        if self.thruster_backward:
            pygame.draw.polygon(
                camera.surface,
                Color("red"),
                [
                    camera.world_to_camera(self.pos + self.radius * p)
                    for p in [forward * 2, left * 1.25, right * 1.25]
                ],
            )

        # "For his neutral special, he wields a gun"
        gun_end = camera.world_to_camera(
            self.pos + forward * self.radius * GUNBARREL_LENGTH
        )
        pygame.draw.line(
            camera.surface,
            Color("blue"),
            ship_screen_pos,
            gun_end,
            int(GUNBARREL_WIDTH * self.radius),
        )

        # thruster_rot_left (material)
        pygame.draw.polygon(
            camera.surface,
            darker_color,
            [
                camera.world_to_camera(self.pos + self.radius * p)
                for p in [
                    0.7 * left + 0.7 * forward,
                    0.5 * left + 0.5 * backward,
                    2.0 * left + 1.0 * backward,
                ]
            ],
        )
        # thruster_rot_left (active)
        if self.thruster_rot_left:
            pygame.draw.polygon(
                camera.surface,
                Color("yellow"),
                [
                    camera.world_to_camera(self.pos + self.radius * p)
                    for p in [
                        1.5 * left + 1.25 * backward,
                        0.5 * left + 0.5 * backward,
                        2.0 * left + 1.0 * backward,
                    ]
                ],
            )

        # thruster_rot_right (material)
        pygame.draw.polygon(
            camera.surface,
            darker_color,
            [
                camera.world_to_camera(self.pos + self.radius * p)
                for p in [
                    0.7 * right + 0.7 * forward,
                    0.5 * right + 0.5 * backward,
                    2.0 * right + 1.0 * backward,
                ]
            ],
        )
        # thruster_rot_right (active)
        if self.thruster_rot_right:
            pygame.draw.polygon(
                camera.surface,
                Color("yellow"),
                [
                    camera.world_to_camera(self.pos + self.radius * p)
                    for p in [
                        1.5 * right + 1.25 * backward,
                        0.5 * right + 0.5 * backward,
                        2.0 * right + 1.0 * backward,
                    ]
                ],
            )

        # thruster_forward (flame)
        if self.thruster_forward:
            pygame.draw.polygon(
                camera.surface,
                Color("orange"),
                [
                    camera.world_to_camera(self.pos + self.radius * p)
                    for p in [
                        0.7 * left + 0.7 * backward,
                        0.5 * left + 1.5 * backward,
                        1.25 * backward,
                        0.5 * right + 1.5 * backward,
                        0.7 * right + 0.7 * backward,
                    ]
                ],
            )
        # thruster_forward (material)
        pygame.draw.polygon(
            camera.surface,
            darker_color,
            [
                camera.world_to_camera(self.pos + self.radius * p)
                for p in [
                    0.7 * left + 0.7 * backward,
                    0.5 * left + 1.25 * backward,
                    1.0 * backward,
                    0.5 * right + 1.25 * backward,
                    0.7 * right + 0.7 * backward,
                ]
            ],
        )

        super().draw(camera)  # Draw circular body ("hitbox")

    # TODO: Either revive or delete this code at some point
    # If reviving, add `self.load_image('ship_sprite.png')` back
    # to the Ship.__init__ method.
    """
    def load_image(self, image_path: str):
        
        #Load and prepare the ship image.
        #param image_path: Path to the ship image file
        
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 28))  # Resize 
        self.original_image = self.image  # Store the original image for rotation

    def draw_with_image(self, screen: pygame.Surface, camera_pos: Vector2): # TODO is this type hinting ???
        ship_relative_pos = self.pos - camera_pos # TODO should all be done using vectors
            
        # Rotate the image
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        
        # Get the rect of the rotated image and set its center
        rect = rotated_image.get_rect()
        rect.center = ship_relative_pos
            
        # Draw the rotated image
        screen.blit(rotated_image, rect)
    """

class BulletEnemy(Ship):
    def __init__(self, pos: Vector2, vel: Vector2):
        super().__init__(pos, vel, 1, 8, Color("purple"))
        self.shoot_cooldown = 0
        self.action_timer = 1 * 60

        self.health = 100

    # TODO: Add return-type to this function
    def step(self, dt: float) -> "Sequence[Bullet]":
        delta = ship.pos - self.pos
        dist = delta.magnitude()
        # TODO: Rather than storing an int for current_action, store some enum. See:
        # https://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
        self.current_action = 6
        force = calculate_gravity(self.pos, 100, planets)  # Assume enemy mass is 100
        self.speed += force / 100
        self.check_planet_collision(planets)

        # Check if period has elapsed
        if self.action_timer <= 0:
            self.current_action = random.randint(1, 4)
            self.action_timer = 0.5 * 60  # Reset timer to seconds

        if self.current_action == 1:  # Accelerate towards player
            self.speed += delta * ENEMY_ACCELERATION * 2 / dist

        elif self.current_action == 2:  # Accelerate randomly
            rand_speed = Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            self.speed += rand_speed * ENEMY_ACCELERATION * 0.2

        elif self.current_action == 3:  # Decelerate
            self.speed.move_towards_ip(Vector2(0, 0), ENEMY_ACCELERATION * 0.2)

        # Update position
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]

        self.action_timer -= 1

        # Shooting logic
        if dist < ENEMY_SHOOT_RANGE and self.shoot_cooldown <= 0:
            if self.type == "bullet":
                # Set cooldown for bullet enemy
                self.shoot_cooldown = BULLET_SHOOT_COOLDOWN
                # TODO: `self` is not of type `Ship`. Perhaps `Enemy` should be subclass of `Ship`?
                return [Bullet(self.pos, self.speed, Color("orange"))]
            else:
                # Set cooldown for rocket enemy
                self.shoot_cooldown = ROCKET_SHOOT_COOLDOWN
                return [Rocket(self.pos, self.speed * 2, Color("red"))]
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        return []