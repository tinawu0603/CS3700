# CS3700: Simple Client

## Project Overview
I implemented a client program which communicates with a server using sockets. The server will ask my program to solve hundreds of simple mathematical expressions. If my program successfully solves all the expressions, a *secret flag* will be returned.

## Project Response

### High level approach
My high level approach for this project is to think about an in-person communication. Once contact is made, whether eye-contact for in-person or socket connection for servers and clients, one side sends an acknowledgement message. Then communication is continued until one side decides to end the communication. In the project, this communication is depicted with the initial HELLO message and then the continuous STATUS messages and ends with a BYE message.

### Challenges I faced
One challenge I faced while working on this project is learning Python and writing networking code. As I have no experience in Python prior to this project, it required reading documentation and learning the syntax of a new language. Another challenge I faced was writing the client program on my local computer and then scp-ing the file to the remote machine, this caused the remote machine not being able to recognize my file.

Another challenge I had during this project was using Vim as my editor. As prior to this class, I've always used an IDE or an advanced text editor like Atom to write my programs. I had to learn specific commands to make writing in Vim easier.

### Overview of how I tested my code
Testing for this program is limited because there is no way to control the STATUS messages the server sends my client. One way I tested my code was testing the computation function separately with print statements to make sure the function is performing the correct operation based on the inputs. Another way I tested my code was printing the messages I receive from the server and again printing the parsed segments to make sure that the segments are parsed correctly.
