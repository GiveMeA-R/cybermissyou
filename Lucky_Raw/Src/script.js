const spinner = document.querySelector('.spinner');
const startBtn = document.querySelector('.spinner__start-button');
const input = document.querySelector('.spinner__input');
const cancelButton = document.querySelector('.cancel-button');
let count = 0;
let plate = document.querySelector('.spinner__plate');
let items = [...document.getElementsByClassName('spinner__item')];
let isSpinning = false;
let cancelledNumbers = new Set();
let appearedNumbers = [];

// Cập nhật giá trị max cho input
input.max = 76; // Cập nhật giá trị max tùy thuộc vào số người tham gia

// Sự kiện thay đổi giá trị input
input.addEventListener('change', e => {
  if (input.value === '' || +input.value < 1) {
    input.value = 1;
  }
  if (+input.value > input.max) {
    input.value = input.max;
  }
});

// Sự kiện click nút Start
startBtn.addEventListener('click', function () {
  if (!isSpinning) {
    randomizeItems();
    isSpinning = true;
    startBtn.disabled = true;
    plate.classList.add('spinner__plate--spin');
    plate.addEventListener('animationend', handleAnimationEnd);
  }
});

// Sự kiện click nút Cancel
cancelButton.addEventListener('click', function () {
  const currentNumber = items[0].textContent;
  cancelNumber(currentNumber);
});

function randomizeItems() {
  items.forEach(item => {
    if (!cancelledNumbers.has(item.textContent)) {
      const rand = getRandomNumber();
      item.textContent = rand;
      appearedNumbers.push(rand);
    }
  });
}

function getRandomNumber() {
  const maxNumber = +input.value;
  let randomNumber = random(1, maxNumber);
  while (appearedNumbers.includes(randomNumber)) {
    randomNumber = random(1, maxNumber);
  }
  return randomNumber;
}

function random(min, max) {
  let rand = min - 0.5 + Math.random() * (max - min + 1);
  return Math.round(rand);
}

function handleAnimationEnd() {
  plate.classList.remove('spinner__plate--spin');
  isSpinning = false;
  startBtn.disabled = false;
  plate.removeEventListener('animationend', handleAnimationEnd);
  const currentNumber = items[0].textContent;
  if (!cancelledNumbers.has(currentNumber)) {
    count++;
    addToLog(count, currentNumber);
    if (count === 10) {
      selectWinningNumbers();
    } else if (count === 13) {
      selectWinningNumbers();
    } else if (count === 14) {
      selectWinningNumbers();
    }
  }
}

function addToLog(count, number) {
  const logTable = document.getElementById('logTable');
  const tbody = logTable.querySelector('tbody');

  // Kiểm tra xem số đã tồn tại trong danh sách đã hủy chưa
  if (cancelledNumbers.has(number)) {
    return; // Bỏ qua việc thêm số vào bảng log
  }

  // Thêm số vào bảng log
  const newRow = document.createElement('tr');
  const countCell = document.createElement('td');
  const numberCell = document.createElement('td');
  const prizeCell = document.createElement('td'); // Thêm cột giải thưởng

  countCell.textContent = count;
  numberCell.textContent = number;

  newRow.appendChild(countCell);
  newRow.appendChild(numberCell);
  newRow.appendChild(prizeCell); // Thêm cột giải thưởng vào hàng

  tbody.appendChild(newRow);

  // Cập nhật mảng appearedNumbers chỉ với các số chưa bị hủy
  appearedNumbers = Array.from(new Set([...appearedNumbers, number])).filter(
    (num) => !cancelledNumbers.has(num)
  );

  // Cập nhật giải thưởng dựa trên số thứ tự của số chưa bị hủy
  if (appearedNumbers.length >= 1 && appearedNumbers.length <= 10) {
    prizeCell.textContent = 'Giải 3';
  } else if (appearedNumbers.length >= 11 && appearedNumbers.length <= 13) {
    prizeCell.textContent = 'Giải 2';
  } else if (appearedNumbers.length === 14) {
    prizeCell.textContent = 'Giải 1';
  } else {
    prizeCell.textContent = ''; // Nếu không thuộc các giải thưởng trên, để cột trống
  }

  // Cập nhật STT của bảng log
  updateSTT(logTable);
}


function cancelNumber(number) {
  items.forEach(item => {
    if (item.textContent === number) {
      item.textContent = '';
      cancelledNumbers.add(number);
    }
  });

  const logTable = document.getElementById('logTable');
  const tbody = logTable.querySelector('tbody');
  const rows = tbody.querySelectorAll('tr');

  rows.forEach(row => {
    const numberCell = row.querySelector('td:nth-child(2)');
    if (numberCell.textContent === number) {
      row.remove();
    }
  });

  // Cập nhật STT của bảng log
  updateSTT(logTable);
}

function updateSTT(logTable) {
  const tbody = logTable.querySelector('tbody');
  const rows = tbody.querySelectorAll('tr');
  rows.forEach((row, index) => {
    const countCell = row.querySelector('td:nth-child(1)');
    countCell.textContent = index + 1;
  });
}

