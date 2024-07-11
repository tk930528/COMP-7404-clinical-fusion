### Adjustments+

We made these adjustments based on our python version==3.8. If your python version is 3.6, I am not sure if some of these changes are necessary.

- Move the file `tools/parse.py` out from the folder and put it into the current working directory.

- In *main.py*: You may find a syntax error in `tensor.cuda(async=True)` if your python version is >=3.7. Update it with `tensor.cuda(non_blocking=True)`. Leave it if there is no syntax error.

- In *main.py*: Delete anything related to `args.unstructure_size`. For the variable `args.use_unstructure`, we have updated the code so it can be used to do ablation study on unstructure text. You can see the details in the code we submitted.

- In *data_loader.py*: Delete anything related to `unstructure_dict`. This variable is useless.

- In *data_loader.py*: If you meet any pattern like `'w'`, change all of them into `'r'`.

- In *lstm.py*, update the variable `args.unstructure_size` with `args.vocab_size`.

- In *cnn.py*, there is a duplicated `if` block about `if content is not None`. Delete the former one. Same for *lstm.py*.

- In *cnn.py*, ignore the `if` block about `if args.use_unstructure`. Run the code inside no matter what `args.use_unstructure` is. Same for *lstm.py*.