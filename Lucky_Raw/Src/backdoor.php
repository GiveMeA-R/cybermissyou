<!DOCTYPE html>
<html>
<head>
    <title>Vòng quay trúng thưởng</title>
    <style>
        .container {
            position: relative;
            width: 600px;
            height: 600px;
            margin: 0 auto;
        }

        .circle {
            position: absolute;
            top: 0;
            left: 0;
            width: 600px;
            height: 600px;
            border-radius: 50%;
            background-color: #f1f1f1;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .triangle {
            position: absolute;
            width: 0;
            height: 0;
            border-left: 300px solid transparent;
            border-right: 300px solid transparent;
            border-bottom: 520px solid #bbb;
            transform-origin: center bottom;
        }

        .number {
            position: absolute;
            top: 30px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 24px;
            font-weight: bold;
            color: #fff;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="circle">
            <?php
            $startNumber = isset($_POST['startNumber']) ? intval($_POST['startNumber']) : 1;
            $endNumber = isset($_POST['endNumber']) ? intval($_POST['endNumber']) : 10;

            $count = $endNumber - $startNumber + 1;
            $angle = 360 / $count;

            for ($i = $startNumber; $i <= $endNumber; $i++) {
                $rotate = ($i - $startNumber) * $angle;
                echo '<div class="triangle" style="transform: rotate(' . $rotate . 'deg);">';
                echo '<div class="number">' . $i . '</div>';
                echo '</div>';
            }
            ?>
        </div>
    </div>

    <form method="post" action="">
        <label for="startNumber">Số bắt đầu:</label>
        <input type="number" name="startNumber" id="startNumber" required>

        <label for="endNumber">Số kết thúc:</label>
        <input type="number" name="endNumber" id="endNumber" required>

        <button type="submit">Bắt đầu quay</button>
    </form>
</body>
</html>
