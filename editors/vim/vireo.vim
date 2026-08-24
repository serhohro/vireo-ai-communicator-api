" [file name]: editors/vim/vireo.vim
" ============================================================
" VIREO SYNTAX FOR VIM/NEOVIM
" ============================================================

if exists("b:current_syntax")
  finish
endif

" Keywords
syn keyword vireoKeyword let const fn return if else for while print
syn keyword vireoKeyword model train predict evaluate agent negotiation contract
syn keyword vireoKeyword import export pub module use

" Types
syn keyword vireoType Tensor Int F32 F64 Bool Str List Dict Signature DID

" Layers
syn keyword vireoLayer Dense Conv2D MaxPool2D BatchNorm Dropout Flatten LSTM
syn keyword vireoLayer Embedding LayerNorm

" Activations
syn keyword vireoActivation ReLU Sigmoid Tanh Softmax Swish

" Optimizers
syn keyword vireoOptimizer SGD Adam CrossEntropy MSE

" Decorators
syn match vireoDecorator "@\w\+"

" Comments
syn region vireoComment start="//" end="$" contains=@Spell
syn region vireoCommentBlock start="/\*" end="\*/" contains=@Spell

" Strings
syn region vireoString start='"' end='"' contains=vireoEscape
syn match vireoEscape '\\[\\"]' contained

" Numbers
syn match vireoNumber '\v<\d+\.?\d*>'

" Operators
syn match vireoOperator '\v[+\-*/=<>!?:]+'

" Functions
syn match vireoFunction '\v[[:alnum:]_]+\([^)]*\)'

" Highlighting
hi def link vireoKeyword Keyword
hi def link vireoType Type
hi def link vireoLayer Function
hi def link vireoActivation Function
hi def link vireoOptimizer Function
hi def link vireoDecorator PreProc
hi def link vireoComment Comment
hi def link vireoCommentBlock Comment
hi def link vireoString String
hi def link vireoNumber Number
hi def link vireoOperator Operator
hi def link vireoFunction Function

let b:current_syntax = "vireo"