class Board {
    static NUM_ROWS = 6;
    static NUM_COLS = 6;
    static SHOW_SOLUTION = false;

    constructor(image, rowHints, colHints) {
        this.image = image;
        this.rowHints = rowHints;
        this.colHints = colHints;
        this.value = [...Array(image.length)].map(e => Array(image[0].length).fill(0));
    }

    static FromHints(rowHints, colHints) {
        const image = Board.calcImage(rowHints, colHints);
        return new Board(image, rowHints, colHints);
    }

    static FromImage(image) {
        const rowHints = Board.calcRowHints(image);
        const colHints = Board.calcColHints(image);
        return new Board(image, rowHints, colHints);
    }

    static FromFlatImage(flat, num_rows, num_cols) {
        let image = [];
        for(let i = 0; i < num_rows; i++) {
            let row = flat.slice(i * num_cols, (i + 1) * num_cols)
            image.push(row.split(''));
        }
        return Board.FromImage(image);
    }

    static RandomBoard(numRows, numCols) {
        let image = [];
        for(let i = 0; i < numRows; i++) {
            image.push(Array.from({length: numCols}, () => Math.floor(Math.random() * 2)))
        }
        return Board.FromImage(image);
    }

    static calcRowHints(image) {
        let out = []
        let max_hints = 0;
        image.forEach((row) => {
            let count = 0;
            let r_h = [];
            for(let i = 0; i < row.length; i++) {
                if(row[i] == '1') {
                    count++;
                }
                else {
                    count !== 0 ? r_h.push(count) : '';
                    count = 0;
                }
            }
            count !== 0 ? r_h.push(count) : '';
            out.push(r_h);
            max_hints = Math.max(max_hints, r_h.length);
        });
        out = out.map((hint) => {
            return [...Array(max_hints - hint.length).fill(0), ...hint];
        });
        return out;
    }

    static calcColHints(image) {
        const rotated = image[0].map((_, colIndex) => image.map(row => row[colIndex]));
        return Board.calcRowHints(rotated);
    }

    static calcImage(rowHints, colHints) {return null;}

    drawBoard(id) {
        let gameBoard = document.querySelector("#" + id);
        gameBoard.innerHTML = '';

        const table = document.createElement("table");
        gameBoard.append(table);
        const thead = document.createElement("thead");
        table.append(thead);

        for(let i = 0; i < this.colHints[0].length; i++) {
            const tr = document.createElement("tr");
            thead.append(tr);
            // prepend empty cells for row hints
            for(let j = 0; j < this.rowHints[0].length; j++) {
                const th = document.createElement("th");
                tr.append(th);
            }
            for(let j = 0; j < this.colHints.length; j++) {
                const th = document.createElement("th");
                th.innerHTML = this.colHints[j][i] === 0 ? '' : this.colHints[j][i];
                tr.append(th);
            }
        }
        const tbody = document.createElement("tbody");
        table.append(tbody);
        for(let i = 0; i < this.rowHints.length; i++) {
            const tr = document.createElement("tr");
            tbody.append(tr);
            for(let j = 0; j < this.rowHints[i].length; j++) {
                const th = document.createElement("th");
                th.innerHTML = this.rowHints[i][j] === 0 ? '' : this.rowHints[i][j];
                tr.append(th);
            }
            for(let j = 0; j < this.colHints.length; j++) {
                const td = document.createElement("td");
                const button = document.createElement("a");
                button.value = "0";
                const div = document.createElement("div");
                const val = document.createElement("param");
                div.id = "cell-" + i + "-" + j;
                val.value = 0;
                div.classList.add('cell', 'cell-unselected');
                button.append(div);
                div.append(val);
                button.onclick = (e) => this.toggleButtonState(e.target, i, j);
                td.append(button);
                tr.append(td);
            }
        }

        const newGameButton = document.createElement("a");
        newGameButton.innerHTML = "<div class='button'>New Board</div>"
        newGameButton.onclick = newGame;
        gameBoard.append(newGameButton);

        const verifyButton = document.createElement("a");
        verifyButton.innerHTML = "<div class='button'>Submit</div>"
        verifyButton.onclick = () => this.verify();
        gameBoard.append(verifyButton);

        const showSolutionButton = document.createElement("a");
        showSolutionButton.id = "showSolutionButton";
        showSolutionButton.innerHTML = "<div class='button'>Show Solution</div>"
        showSolutionButton.onclick = () => this.showImage();
        showSolutionButton.style.display = Board.SHOW_SOLUTION ? 'inherit' : 'none';
        gameBoard.append(showSolutionButton);

        const p = document.createElement("p");
        p.id = "verify-output"
        gameBoard.append(p)

    }

    toggleButtonState(target, i, j) {
        const param = target.firstChild;
        param.value = (param.value + 1) % 3;
        this.setButtonState(target, i, j, param.value);
    }
    setButtonState(target, i, j, state) {
        this.value[i][j] = state;
        switch(state) {
            case '0':
                target.classList.remove('cell-selected', 'cell-flagged');
                target.classList.add('cell-unselected');
                break;
            case '1':
                target.classList.remove('cell-unselected', 'cell-flagged');
                target.classList.add('cell-selected');
                break;
            case '2':
                target.classList.remove('cell-selected', 'cell-unselected');
                target.classList.add('cell-flagged');
                break;
            default:
                break;
        }
    }

    verify() {
        const verify_output = document.querySelector("#verify-output");
        const rows = Board.calcRowHints(this.value);
        const cols = Board.calcColHints(this.value);
        if(rows.sort().join(',') === this.rowHints.sort().join(',') &&
           cols.sort().join(',') === this.colHints.sort().join(',')
        ) {
            verify_output.innerHTML = "WINNER";
            document.querySelectorAll(".cell").forEach((e) => {
                e.classList.remove("win");
                void e.offsetWidth;
                e.classList.add("win");
            });
        }
        else {
            verify_output.innerHTML = "Not quite, try again";
            const game = document.querySelector("#game");
            game.classList.remove("shake");
            void game.offsetWidth;
            game.classList.add("shake");
        }
    }

    showImage() {
        for(let i = 0; i < this.image.length; i++) {
            for(let j = 0; j < this.image[0].length; j++) {
                const cell = document.querySelector("#cell-" + i + "-" + j);
                this.setButtonState(cell, i, j, this.image[i][j].toString());
            }
        }
    }
}


function newGame() {
    const board = Board.RandomBoard(Board.NUM_ROWS, Board.NUM_COLS);
    board.drawBoard("game");
}


function openNav() {
    document.querySelector("#settingsNav").style.width = "100%";
}

function closeNav() {
    const temp1 = Board.NUM_ROWS;
    const temp2 =  Board.NUM_COLS;
    Board.NUM_ROWS = document.querySelector("#setting-num-rows").value;
    Board.NUM_COLS = document.querySelector("#setting-num-cols").value;
    Board.SHOW_SOLUTION = document.querySelector("#setting-show-solution").checked;
    document.querySelector("#showSolutionButton").style.display = Board.SHOW_SOLUTION ? 'inherit' : 'none';

    if(temp1 != Board.NUM_ROWS || temp2 != Board.NUM_COLS) {
        document.querySelector("#verify-output").innerHTML = "Start a new game for changes to take effect";
    }

    document.querySelector("#settingsNav").style.width = "0%";
}

const arrayColumn = (arr, n) => arr.map(x => x[n]);

newGame();

