import re
import sys
import uuid
import unittest
from subprocess import Popen, PIPE, STDOUT
from repoman_client.__version__ import version

class RepomanCLITest(unittest.TestCase):
    """
    Base class for all Repoman CLI tests.
    """

    def setUp(self):
        # Nothing to do for now...
        pass

    def tearDown(self):
        # Nothing to do for now...
        pass

    def run_repoman_command(self, args):
        """
        This method will call the repoman application in a subprocess
        and pass it the given command line argument string.
        The output and the return code of the repoman invocation will be
        returned to the caller for further inspection.
        """
        try:
            cmd = 'repoman %s' % (args)
            print 'Running [%s]' % (cmd)
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
            output = p.communicate()[0]
            return (output, p.returncode)
        except Exception, e:
            print 'Error running repoman command.\n%s' % (e)
            sys.exit(-1)
            

    def get_unique_image_name(self):
        """
        Use this method to easily create a unique image name to use in 
        your tests.
        """
        return str(uuid.uuid1())




#####################################################################
#####################################################################
#####################################################################
#
# Test cases implementation go here...
#
#


#***********************************************************************************************#
#                               MISCELLANEOUS SUBCOMMANDS                                       #
#***********************************************************************************************#



#####################################################################
#		COMMAND - 'repoman about'
#####################################################################


class AboutTest(RepomanCLITest):
    def test_about(self):
	(output, returncode) = self.run_repoman_command('about')
	p = re.search(r'client version:.*\n\s*config files in use:.*\n\s*repository_host:.*\n\s*repository_port:.*\n\s*user_proxy_cert:.*\n\s*snapshot:.*\n\s*mountpoint:.*\n\s*lockfile:.*\n\s*system_excludes:.*\n\s*user_excludes:.*\n\s*logging:', output)
	self.assertEqual(returncode, 0)
	self.assertTrue( p != None)


######################################################################
#		COMMAND - 'repoman version'
######################################################################


class ClientVersionTest(RepomanCLITest):
    def test_version(self):
        (output, returncode) = self.run_repoman_command('version')
        self.assertEqual(output, '%s\n' % (version))
        self.assertEqual(returncode, 0)


######################################################################
#		COMMAND - 'repoman whoami'
######################################################################


class WhoamiTest(RepomanCLITest):
    def test_whoami(self):
        (output, returncode) = self.run_repoman_command('whoami')
        self.assertEqual(returncode, 0)




#***********************************************************************************************#
#                               IMAGE MANUPILATION SUBCOMMANDS                                  #
#***********************************************************************************************#



def CheckOptions(self, output, arg): 			
	"""
	CheckOptions method tests the common optional parameters for create-image and modify-image
	"""

	# If unauthenticated access is set as true or false while creating or modifying an image,
	# the status is checked in the output of 'repoman list-images' using regular expression 	
	if(arg == "--unauthenticated_access true" or arg == "-a true"):
		p = re.search('^\\s*unauthenticated_access : True\\s*$', output,flags=re.MULTILINE)
		self.assertTrue(p != None) 
	elif (arg == '--unauthenticated_access false' or arg == '-a false'):
                p = re.search('^\\s*unauthenticated_access : False\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)
	
	# If a description is given as "Random discription" while creating or modifying an image, 
	# the corresponding description is checked in the output of 'repoman list-images'
	elif (arg == '--description "Random description"' or arg == '--d "Random description"'):
		p = re.search('^\\s*description : Random description\\s*$', output, flags=re.MULTILINE)
		self.assertTrue(p != None)
	
	# If the hypervisor is set to or changed to a particular value (here 'xen'), it is checked in the output
	# of 'repoman list-images'
	elif (arg =='--hypervisor xen' or arg == '-h "xen"'):
		p = re.search('^\\s*hypervisor : xen\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)
	
	# If the Operating System Architecture is set to or changed to a particular value (here 'x86'),
	# the corresponding output is checked in 'repoman list-images'
        elif (arg =='--os_arch x86'):
                p = re.search('^\\s*os_arch : x86\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)

        # If the Operating System type is set to or changed to a particular value (here 'linux'),
        # the corresponding output is checked in 'repoman list-images'
        elif (arg =='--os_type linux'):
                p = re.search('^\\s*os_type : linux\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)

        # If the Operating System Variant is set to or changed to a particular value (here 'ubuntu'),
        # the corresponding output is checked in 'repoman list-images'
        elif (arg =='--os_variant ubuntu'):
                p = re.search('^\\s*os_variant : ubuntu\\s*$', output, flags=re.MULTILINE)
                self.assertTrue(p != None)



######################################################################
#		COMMAND - 'repoman create-image'		     	
######################################################################



class CreateImageTest(RepomanCLITest):
    new_image_name = None
	
    def CreateImage(self, arg):
	"""
    	CreateImage method is called whenever the create-image command is used (with or without optional parameters)
    	Optional parameters are stored in arg. 
    	When create-image is called without options, arg is passed as an empty string
    	"""
        # Get a unique name for the new image we are going to create.
        # This will ensure it does not clash with any existing image on the
        # server.
        self.new_image_name = self.get_unique_image_name()
	
        # Now let's run the 'repoman create-image' command and check it's
        # output and exit code.
        (output, returncode) = self.run_repoman_command('create-image %s %s' % (self.new_image_name, arg))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)

        # Here we actually do a 'repoman list-image' to see if the image is
        # actually there.  We use a regular expression to inspect the output.
        (output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
        m = re.search('^\\s+name : %s\\s*$' % (self.new_image_name), 
                      output, 
                      flags=re.MULTILINE)
        self.assertTrue(m != None)        
	
	CheckOptions(self, output, arg)


    def tearDown(self):
        # Delete the image we created to clean up properly after the test.
       	(output, returncode) = self.run_repoman_command('remove-image -f %s' % (self.new_image_name))

   
    def test_create_image(self):
	CreateImageTest.CreateImage(self,'')

    
    # Test the alias of create-image command ('repoman ci')	
    def test_ci(self):	
	self.new_image_name = self.get_unique_image_name()
	(output, returncode) = self.run_repoman_command('ci %s' % (self.new_image_name))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)
	(output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
        m = re.search('^\\s+name : %s\\s*$' % (self.new_image_name),
                      output,
                      flags=re.MULTILINE)
        self.assertTrue(m != None)


	#########################################################
	#		OPTIONAL PARAMETERS			#	
	#########################################################

    # Test the optional parameter '--unauthenticated_access' or '-a', which can be set to true or false
    # Each case is in individual tests to ensure teardown (removing image after creating one)
    def test_create_image_unauthenticated_access_true(self):
	CreateImageTest.CreateImage(self,'--unauthenticated_access true')
    def test_create_image_a_true(self):		
	CreateImageTest.CreateImage(self,'-a true')
    def test_create_image_unauthenticated_access_false(self):
	CreateImageTest.CreateImage(self,'--unauthenticated_access false')       
    def test_create_image_a_false(self):   
	CreateImageTest.CreateImage(self,'-a false')


    # Test the optional parameter '--description' or '-d' 
    # The description given here is "Random description"
    def test_create_image_description(self):
	CreateImageTest.CreateImage(self, '--description "Random description"')
    def test_create_image_d(self):
        CreateImageTest.CreateImage(self, '--d "Random description"')
 
	
    # Test the optional parameter '--hypervisor' or '-h'
    # For this test, a random hypervisor ('xen') is selected
    def test_create_image_hypervisor(self):
	CreateImageTest.CreateImage(self, '--hypervisor xen')
    def test_create_image_h(self):
	CreateImageTest.CreateImage(self, '-h "xen"') 
	
    # Test the optional parameter '--os_arch'
    # For this test, a random operating system architecture ('x86') is selected
    def test_create_image_os_arch(self):
	CreateImageTest.CreateImage(self, '--os_arch x86')	

    # Test the optional parameter '--os_type'
    # For this test, a random operating system type ('linux') is selected
    def test_create_image_os_type(self):
        CreateImageTest.CreateImage(self, '--os_type linux')

    # Test the optional parameter '--os_variant'
    # For this test, a random operating system type ('ubuntu') is selected
    def test_create_image_os_variant(self):
        CreateImageTest.CreateImage(self, '--os_variant ubuntu')

    def CreateImageFile(self, arg):
	"""
	CreateImageFile method tests the optional parameters '--file' or '-f', which creates an image by uploading a file
	It tests the optional parameter passed to arg. arg can be '--file' or '-f'
	"""
	# Get a unique name for the image and a dummy file that will be uploaded
	self.new_image_name = self.get_unique_image_name()
	random_file = self.get_unique_image_name()
	# Create a dummy file of 10 MB(10485760 bytes) with a unique name
	p = Popen('dd if=/dev/zero of=%s bs=10485760 count=1' % (random_file), shell=True, stdout=PIPE, stderr=STDOUT)
	output = p.communicate()[0]
	self.assertEqual(p.returncode, 0)
	
        # Try optional parameters '--file' or '-f' with the unique name generated above as the name of the image
	(output, returncode) = self.run_repoman_command('create-image %s %s %s' % (self.new_image_name, arg, random_file))
	p = re.search(r'.+OK.+ Created new image.+\nUploading %s to new image.+\n.+OK.+%s uploaded to image.+' % (random_file, random_file), output)       
	self.assertTrue(p != None)
        self.assertEqual(returncode, 0)

        # Here we actually do a 'repoman list-image' to see if the image is
        # actually there.  We use a regular expression to inspect the output.
        (output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
        m = re.search('^\\s+name : %s\\s*$' % (self.new_image_name), output, flags=re.MULTILINE)
        self.assertTrue(m != None)
	
	# Change the unauthenticated access to true so that the file can be downloaded
	(output, returncode) = self.run_repoman_command('modify-image %s --unauthenticated_access true' % (self.new_image_name))
	self.assertEqual(returncode, 0)

	# Retrieve the url of the file and and download it using wget
	(output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
	self.assertEqual(returncode, 0)
	m = re.findall(r'http://.+', output)
	p = Popen('wget %s' % (m[0]), shell=True, stdout=PIPE, stderr=STDOUT)
 	output = p.communicate()[0]
        self.assertEqual(p.returncode, 0)
	
	# Check if that file got uploaded and consequently downloaded matches the original file
	p = Popen('diff %s %s' % (random_file, self.new_image_name), shell=True, stdout=PIPE, stderr=STDOUT)
        output = p.communicate()[0]
	self.assertEqual(p.returncode, 0)
	
	# Delete the dummy file (random_file) and the downloaded file
	p = Popen('rm %s %s' % (random_file, self.new_image_name), shell=True, stdout=PIPE, stderr=STDOUT)
        output = p.communicate()[0]
	self.assertEqual(p.returncode, 0)


#    def test_create_image_file(self):
#	CreateImageTest.CreateImageFile(self, '--file')

#    def test_create_image_f(self):
#	CreateImageTest.CreateImageFile(self, '-f')



		
######################################################################
#               COMMAND - 'repoman modify-image'                        
######################################################################



class ModifyImageTest(RepomanCLITest):
    new_image_name = None
    	
    def ModifyImage(self, arg):
	"""
    	ModifyImage function is called whenever the modify-image command is used (with or without optional parameters)
    	Optional parameters are stored in arg. 
    	When modify-image is called without options, arg is passed as an empty string
	"""


        # Get a unique name for the new image we are going to create.
        # This will ensure it does not clash with any existing image on the
        # server.
        self.new_image_name = self.get_unique_image_name()

        # Create a new image to be modified
        (output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)
	
	# 'random_name' variable stores the new name for an image when '-n' or '--new_name' parameters are used
	# It is used to prevent removal of the image with the original name (which wouldn't exist after the name is changed,
	# in the tearDown method. The default is set to None
	global random_name
	random_name = None
	if (arg == '--new_name ' or arg == '-n '):
		
		random_name = self.get_unique_image_name()
		arg = arg + random_name
	# If arg is --new_owner or -n parameter, create a new test user to be the new owner of the modified image
	# For creating the test user, generate two unique names for the first and last names. The first name is used 
	# for the username, email address of the user. The last name is used in the client dn and full name fields.
	if (arg == '--new_owner' or arg == '-N'):
		self.first_name = self.get_unique_image_name()
		self.last_name = self.get_unique_image_name()		
		(output, returncode) = self.run_repoman_command('create-user %s "/C=CA/O=Grid/OU=phys.UVic.CA/CN=%s %s" --email %s@random.com --full_name "%s %s"' % (self.first_name,self.first_name, self.last_name,self.first_name, self.first_name ,self.last_name))
        	self.assertEqual(returncode, 0)
		# add the username of the new owner to arg
		arg = arg + ' ' + self.first_name
	# If the arg is --owner or -o, the username of the current owner is retreived using the 'repoman whoami' command
	# The owner parameter is used with the current user to check whether the it works properly though omitting it in this case
	# would be the same as the default 	
	if (arg == '--owner' or arg == '-o'):
		(output, returncode) = self.run_repoman_command('whoami')
		arg = arg + ' ' + output
	# Run 'repoman modify-image' and check the output
	(output, returncode) = self.run_repoman_command('modify-image %s %s' %(self.new_image_name, arg))
	self.assertEqual(output, "[OK]     Modifying image.\n")
	self.assertEqual(returncode, 0)
	
	if (arg == '--new_name %s' % (random_name) or arg == '-n %s' % (random_name)):
		(output, returncode) = self.run_repoman_command('list-images %s' % (random_name))
		p = re.search('^\\s*name : %s\\s*$' % (random_name), output, flags=re.MULTILINE)
                self.assertTrue(p != None)
		
	if (re.search('--new_owner', arg) or re.search('-N', arg)):
		(output, returncode) = self.run_repoman_command('list-images %s --owner %s' % (self.new_image_name, self.first_name))
		p = re.search('^\\s*owner : %s\\s*$' % (self.first_name), output, flags=re.MULTILINE)
		self.assertTrue(p != None)	
		(output, returncode) = self.run_repoman_command('remove-user --force %s' % (self.first_name))	
	
	# Call CheckOptions to check some common optional parameters of create-image and modify-image
	if(random_name == None):
		(output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
		CheckOptions(self, output, arg)
	
	
	
    def tearDown(self):
	if (random_name != None):
		(output, returncode) = self.run_repoman_command('remove-image -f %s' % (random_name))
	else:
		# Delete the image we created to clean up properly after the test.
        	(output, returncode) = self.run_repoman_command('remove-image -f %s' % (self.new_image_name))
		
    def test_modify_image(self):
	ModifyImageTest.ModifyImage(self, '')
    
    # Test the alias of modify-image ('repoman mi')		
    def test_mi(self):
	global random_name
	random_name  = None
	self.new_image_name = self.get_unique_image_name()
	 # Create a new image to be modified
        (output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
        self.assertEqual(output, "[OK]     Created new image '%s'\n" % (self.new_image_name))
        self.assertEqual(returncode, 0)
        # Run 'repoman modify-image' and check the output
        (output, returncode) = self.run_repoman_command('mi %s' %(self.new_image_name))
        self.assertEqual(output, "[OK]     Modifying image.\n")
        self.assertEqual(returncode, 0)	


        #########################################################
        #               OPTIONAL PARAMETERS                     #       
        #########################################################


    # Test the optional parameter '--unauthenticated_access' or '-a', which can be set to true or false
    # All the different cases are in individual tests to ensure teardown (removal of image after creating one)
    def test_modify_image_unauthenticated_access_true(self):
        ModifyImageTest.ModifyImage(self,'--unauthenticated_access true')
    def test_modify_image_a_true(self):
        ModifyImageTest.ModifyImage(self,'-a true')
    def test_modify_image_unauthenticated_access_false(self):
        ModifyImageTest.ModifyImage(self,'--unauthenticated_access false')
    def test_modify_image_a_false(self):
        ModifyImageTest.ModifyImage(self,'-a false')


    # Test the optional parameter '--description' or '-d' 
    # The description given here is "Random description"
    def test_modify_image_description(self):
        ModifyImageTest.ModifyImage(self, '--description "Random description"')
    def test_modify_image_d(self):
        ModifyImageTest.ModifyImage(self, '--d "Random description"')


    # Test the optional parameter '--hypervisor' or '-h'
    # For this test, a random hypervisor ('xen') is selected
    def test_modify_image_hypervisor(self):
        ModifyImageTest.ModifyImage(self, '--hypervisor xen')
    def test_modify_image_h(self):
        ModifyImageTest.ModifyImage(self, '-h "xen"')

    
    # Test the optional parameter '--new_name' or '-n'
    # A random name is kept as the new name which is generated later in the method ModifyImage
    def test_modify_image_new_name(self):
	ModifyImageTest.ModifyImage(self, '--new_name ')
    def test_modify_image_n(self):
	ModifyImageTest.ModifyImage(self, '-n ')		


    # Test the optional parameter '--new_owner' or '-N'
    # A test user is created in the method ModifyImage which is used as the new owner for the image
    def test_modify_image_new_owner(self):
	ModifyImageTest.ModifyImage(self, '--new_owner')
    def test_modify_image_N(self):
	ModifyImageTest.ModifyImage(self, '-N')	


    # Test the optional parameter '--owner' or '-o'
    # The owner used is the current owner which is the same as the output for 'repoman whoami'
    def test_modify_image_owner(self):
	ModifyImageTest.ModifyImage(self, '--owner')
    def test_modify_image_o(self):
	ModifyImageTest.ModifyImage(self, '-o')

    # Test the optional parameter '--os_arch'
    # For this test, a random operating system architecture ('x86') is selected
    def test_modify_image_os_arch(self):
        ModifyImageTest.ModifyImage(self, '--os_arch x86')

    # Test the optional parameter '--os_type'
    # For this test, a random operating system type ('linux') is selected
    def test_modify_image_os_type(self):
        ModifyImageTest.ModifyImage(self, '--os_type linux')

    # Test the optional parameter '--os_variant'
    # For this test, a random operating system type ('ubuntu') is selected
    def test_modify_image_os_variant(self):
        ModifyImageTest.ModifyImage(self, '--os_variant ubuntu')

    




#####################################################################
# 		COMMAND - 'repoman list-images'
#####################################################################




class ListImagesTest(RepomanCLITest):

    new_image_name = None
    def ListImages(self, command, arg):
	"""
	The method ListImages is used for the list-images command. It is called with two arguments - command and arg. 
	Command stores either the command name ('list-images') or its alias ('li'), and arg stores the optional parameters.
	The optional parameters are passed as empty strings when the 'repoman list-images' and 'repoman li' are used.
	"""
	# Get a unique name for the image to be created
	self.new_image_name = self.get_unique_image_name()

	# Create the new image and check if it is correctly created
	(output, returncode) = self.run_repoman_command("create-image %s" % (self.new_image_name))
	self.assertEqual(returncode, 0)

	# Run the repoman command for listing images (with or without optional parameters)
	(output, returncode) = self.run_repoman_command("%s %s" % (command, arg))
	p = re.search(self.new_image_name, output)
	self.assertTrue( p != None)
	self.assertEqual(returncode, 0)

	# Check the expected fields if the optional parameters '--long' or '-l' is selected
	if ( arg == '--long' or arg == '-l'):
		p = re.search(r'\s*Image\s*Name\s*Owner\s*Hypervisor\s*Size\s*Last Modified\s*Description', output)
		self.assertTrue( p != None)
	
	# Check if a url is printed if the optional parameter '--url' or '-U' is selected
	if ( arg == '--url' or arg == '-U'):
		p = re.search(r'http', output)
		self.assertTrue( p!= None)


	
    # Delete the image created for each test in class ListImagesTest
    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-image -f %s' %(self.new_image_name))

    def test_list_images(self):
	ListImagesTest.ListImages(self, 'list-images', '')	

    # Test the alias of list-image ('li')
    def test_li(self):
	ListImagesTest.ListImages(self, 'li', '')



        #########################################################
        #               OPTIONAL PARAMETERS                     #       
        #########################################################



    # This tests the optional parameters '--all' and '-a'
    # The test passes if the created image is found in the output
    def test_list_images_all(self):
	ListImagesTest.ListImages(self, 'list-images', '--all')
    def test_list_images_a(self):
	ListImagesTest.ListImages(self, 'list-images', '-a')	
  
    # This tests the optional parameters '--long' and 'a'
    # The expected fields are checked
    def test_list_images_long(self):
        ListImagesTest.ListImages(self, 'list-images', '--long')
    def test_list_images_l(self):
        ListImagesTest.ListImages(self, 'list-images', '-l')

    # This tests the optional parameters '--url' and '-U'
    # Checks for the presence of the string 'http' which may be either 'http://....' or 'https://....'
    def test_list_images_url(self):
        ListImagesTest.ListImages(self, 'list-images', '--url')	
    def test_list_images_U(self):
        ListImagesTest.ListImages(self, 'list-images', '-U')


	
    def ListImagesGroup(self, arg):
	"""
	This method is called for the optional parameters '-g' and '--group'. Here an image is created with a unique name which is shared with the group "users".
	The test is successful if the shared image is listed with the command 'list-images --group users' or 'list-images -g users'
	"""
	self.new_image_name = self.get_unique_image_name()
        (output, returncode) = self.run_repoman_command("create-image %s" % (self.new_image_name))
        self.assertEqual(returncode, 0)
	(output, returncode) = self.run_repoman_command("share-image-with-groups %s users" % (self.new_image_name))
        self.assertEqual(returncode, 0)
        (output, returncode) = self.run_repoman_command("list-images %s users" % (arg))
	p = re.search(self.new_image_name, output)
        self.assertTrue( p != None)


    # Test the optional parameters '--group' and '-g'
    # The image is shared with the group 'users'
    def test_list_images_group(self):
	ListImagesTest.ListImagesGroup(self, '--group')	
    def test_list_images_g(self):
        ListImagesTest.ListImagesGroup(self, '-g')


    # Used for optional parameters 'image', '--owner' and '-o' (where the description of the image is outputted)
    def ListImagesDesc(self, arg):
	"""
        This test runs the 'repoman list-images image' command, and checks if all the fields of the output match the expected fields of the image
        """
        self.new_image_name = self.get_unique_image_name()
        (output, returncode) = self.run_repoman_command("create-image %s" % (self.new_image_name))
        self.assertEqual(returncode, 0)

        # Check if the output is of the proper format
        (output, returncode) = self.run_repoman_command("list-images %s %s" % (self.new_image_name, arg))
        p = re.search(r'checksum :.*\n\s*description :.*\n\s*expires :.*\n\s*file_url :.*\n\s*http_file_url :.*\n\s*hypervisor :.*\n\s*modified :.*\n\s*name : %s.*\n\s*os_arch :.*\n\s*os_type :.*\n\s*os_variant :.*\n\s*owner :.*\n\s*owner_user_name :.*\n\s*raw_file_uploaded :.*\n\s*read_only :.*\n\s*shared_with :.*\n\s*size :.*\n\s*unauthenticated_access :.*\n\s*uploaded :.*\n\s*uuid :.*\n\s*version :' % (self.new_image_name), output)
        self.assertTrue( p != None)
        self.assertEqual(returncode, 0)

    # Test the optional parameter 'image'
    def test_list_images_image(self):
	ListImagesTest.ListImagesDesc(self, '')

    # Test the optional parameters '--owner' and '-o'. Here the owner is passed as the current user just to test the optional parameter
    def test_list_images_owner(self):
	(output, returncode) = self.run_repoman_command('whoami')
	ListImagesTest.ListImagesDesc(self, '--owner %s' % (output))
    def test_list_images_o(self):
        (output, returncode) = self.run_repoman_command('whoami')
        ListImagesTest.ListImagesDesc(self, '-o %s' % (output))

    def ListImagesUser(self, arg):
	"""
	This method is called for the optional parameters '-u' or '--user'. Here an image is created with a unique name, and is shared with a test user with unique 
	first and last names. The test is successful if the shared image is listed with the command 'list-images --user user' or 'list-images -u user'
	"""
	# Get unique names for the image, first name, and last name
	self.new_image_name = self.get_unique_image_name()
	self.first_name = self.get_unique_image_name()
	self.last_name = self.get_unique_image_name()
	# Create the image
	(output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
	self.assertEqual(returncode, 0)
	# Create the test user. The first name is used as the username and email address. The last name is used in the DN and full_name fields
	(output, returncode) = self.run_repoman_command('create-user %s "/C=CA/O=Grid/OU=phys.UVic.CA/CN=%s %s" --email %s@random.com --full_name "%s %s"' % (self.first_name,self.first_name, self.last_name,self.first_name, self.first_name ,self.last_name))
	self.assertEqual(returncode, 0)
	# Share the image with the test user
	(output, returncode) = self.run_repoman_command('share-image-with-users %s %s' % (self.new_image_name, self.first_name))
	self.assertEqual(returncode, 0)
	# Check if the image is seen in list-images
	(output, returncode) = self.run_repoman_command('list-images %s %s' % (arg, self.first_name))
	p = re.search(self.new_image_name, output)
	self.assertTrue(p != None)
	self.assertEqual(returncode, 0)
	# Remove the test user
	(output, returncode) = self.run_repoman_command('remove-user --force %s' % (self.first_name))

    # Test the optional parameter '--user'
    def test_list_images_user(self):
	ListImagesTest.ListImagesUser(self, '--user')
	
    # Test the optional parameter '-u'
    def test_list_images_u(self):
	ListImagesTest.ListImagesUser(self, '-u')
	


#####################################################################
#               COMMAND - 'repoman put-image'
#####################################################################



class PutImageTest(RepomanCLITest):

    def PutImage(self, command, arg):
	"""
	This method is called when the repoman command 'put-image' or 'pi' is called.
	Here a dummy file is created which is uploaded to an existing image slot, and is then downloaded to check 
	if it matches with the original dummy file
	"""
	
	# Get a unique name for the image and a dummy file that will be uploaded
        self.new_image_name = self.get_unique_image_name()
        random_file = self.get_unique_image_name()
        # Create a dummy file of 10 MB(10485760 bytes) with a unique name
        p = Popen('dd if=/dev/zero of=%s bs=10485760 count=1' % (random_file), shell=True, stdout=PIPE, stderr=STDOUT)
        output = p.communicate()[0]
        self.assertEqual(p.returncode, 0)

        # Create the image where the file is to be uploaded
        (output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
        self.assertEqual(returncode, 0)

	# If the '--owner' or '-o' parameters are not passed, the first command for put-image runs without any optional parameters (arg)
	# Uploading the dummy file is also required for the '--force' or '-f' parameters since its meant to overwrite the existing image file	
	if (re.search('-o', arg) == None):
	        # Upload the file with the 'put-image' or 'pi' command into the newly created image
        	(output, returncode) = self.run_repoman_command('%s %s %s' % (command,random_file, self.new_image_name ))
        	p = re.search(r'Uploading %s to image.+\n.*OK.*%s uploaded to image' % (random_file, random_file), output)
		self.assertTrue( p != None)
		self.assertEqual(returncode, 0)
	# Include '--owner' or '-o' parameters if they are passed in arg
	else:
		(output, returncode) = self.run_repoman_command('%s %s %s %s' % (command,random_file, self.new_image_name, arg ))
                p = re.search(r'Uploading %s to image.+\n.*OK.*%s uploaded to image' % (random_file, random_file), output)
                self.assertTrue( p != None)
                self.assertEqual(returncode, 0)
	
	if (arg == '' or re.search('-o', arg)):
	        # Change the unauthenticated access to true so that the file can be downloaded
        	(output, returncode) = self.run_repoman_command('modify-image %s --unauthenticated_access true' % (self.new_image_name))
        	self.assertEqual(returncode, 0)

        	# Retrieve the url of the file and and download it using wget
        	(output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
        	self.assertEqual(returncode, 0)
        	m = re.findall(r'http://.+', output)
        	p = Popen('wget %s' % (m[0].replace('__hypervisor__','xen')), shell=True, stdout=PIPE, stderr=STDOUT)
        	output = p.communicate()[0]
        	self.assertEqual(p.returncode, 0)

        	# Check if the file that got uploaded and consequently downloaded matches the original file
        	p = Popen('diff %s %s' % (random_file, self.new_image_name), shell=True, stdout=PIPE, stderr=STDOUT)
        	output = p.communicate()[0]
        	self.assertEqual(p.returncode, 0)

        	# Delete the dummy file (random_file) and the downloaded file
        	p = Popen('rm %s %s' % (random_file, self.new_image_name), shell=True, stdout=PIPE, stderr=STDOUT)
        	output = p.communicate()[0]
        	self.assertEqual(p.returncode, 0)
	
	elif (arg == '--force' or arg == '-f'):
		# Get a unique name for the new dummy file (new_random_file)
		new_random_file = self.get_unique_image_name()
		
		# Create the new dummy file of 8 MB (8388608 bytes) with the unique name
		p = Popen('dd if=/dev/zero of=%s bs=8388608 count=1' % (new_random_file), shell=True, stdout=PIPE, stderr=STDOUT)
	        output = p.communicate()[0]
        	self.assertEqual(p.returncode, 0)

		# Upload the new dummy file (new_random_file) forcefully to the existing image(self.new_image_name)
		# This action is done forcefully on the image which was identical to the first dummy file (random_file)
		(output, returncode) = self.run_repoman_command('%s %s %s %s' % (command, arg, new_random_file, self.new_image_name ))
		p = re.search(r'Uploading %s to image.+\n.*OK.*%s uploaded to image' % (new_random_file, new_random_file), output)
        	self.assertTrue( p != None)
	        self.assertEqual(returncode, 0)
		
		# Change the unauthenticated access to true so that the file can be downloaded
                (output, returncode) = self.run_repoman_command('modify-image %s --unauthenticated_access true' % (self.new_image_name))
                self.assertEqual(returncode, 0)

                # Retrieve the url of the file and and download it using wget
                (output, returncode) = self.run_repoman_command('list-images %s' % (self.new_image_name))
                self.assertEqual(returncode, 0)
                m = re.findall(r'http://.+', output)
                p = Popen('wget %s' % (m[0].replace('__hypervisor__','xen')), shell=True, stdout=PIPE, stderr=STDOUT)
                output = p.communicate()[0]
                self.assertEqual(p.returncode, 0)

                # Check if the new file that got uploaded and consequently downloaded matches the original file (second dummy file)
                p = Popen('diff %s %s' % (new_random_file, self.new_image_name), shell=True, stdout=PIPE, stderr=STDOUT)
                output = p.communicate()[0]
                self.assertEqual(p.returncode, 0)

                # Delete the dummy files (random_file and new_random_file) and the downloaded file
                p = Popen('rm %s %s %s' % (random_file, new_random_file, self.new_image_name), shell=True, stdout=PIPE, stderr=STDOUT)
                output = p.communicate()[0]
                self.assertEqual(p.returncode, 0)


    def test_put_image(self):
	PutImageTest.PutImage(self, 'put-image', '')

    # Test the alias of put-image ('pi')
    def test_pi(self):
	PutImageTest.PutImage(self, 'pi', '')

    # Test the optional parameters '--force' and '-f'
    def test_put_image_force(self):
	PutImageTest.PutImage(self, 'put-image', '--force')
    def test_put_image_f(self):
        PutImageTest.PutImage(self, 'put-image', '-f')

    # Test the optional parameters '--owner' and '-o'
    def test_put_image_owner(self):
	(output, returncode) = self.run_repoman_command('whoami')
	PutImageTest.PutImage(self, 'put-image', '--owner %s' % (output))
    def test_put_image_o(self):
	(output, returncode) = self.run_repoman_command('whoami')
        PutImageTest.PutImage(self, 'put-image', '-o %s' % (output))

	
    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-image -f %s' %(self.new_image_name))	




#####################################################################
#               COMMAND - 'repoman remove-image'
#####################################################################


class RemoveImageTest(RepomanCLITest):

    def RemoveImage(self, command, arg):
	"""
	This method is called whenever the commands 'remove-image' or 'ri' is used.  
	The argument 'command' can have the value 'remove-image' or 'ri'. 'arg' stores optional parameters
	"""
	# Get a unique name for the image	
	self.new_image_name = self.get_unique_image_name()
	
	# Create a new image to be removed
	(output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
	self.assertEqual(returncode, 0)

	if (arg == '' or re.search('-o', arg)):
		# Run the 'remove-image' or 'ri' command. The 'yes yes' is used to pass 'yes' to the confirmation prompt
		# Here the function run_repoman_command is not used since 'yes yes |' has to precede 'repoman'.
		p = Popen('yes yes | repoman %s %s %s' % (command, self.new_image_name, arg), shell=True, stdout=PIPE, stderr=STDOUT)
        	output = p.communicate()[0]
		m = re.search(r'OK.*Removed image', output)
		self.assertTrue( m != None)
		self.assertEqual(p.returncode, 0)
	elif (arg == '--force' or arg == '-f'):
		# Run 'repoman remove-image --force' or 'repoman remove-image -f' 
        	(output, returncode) = self.run_repoman_command('%s %s %s' % (command, arg, self.new_image_name))
        	m = re.search(r'OK.*Removed image', output)
        	self.assertTrue( m != None)
	        self.assertEqual(returncode, 0)

	
	# Check if the image is removed and can't be seen in list-images
	(output, returncode) = self.run_repoman_command('list-images')
	m = re.search(self.new_image_name, output)
	self.assertTrue( m == None)

    # Test the 'repoman remove-image' command
    def test_remove_image(self):
	RemoveImageTest.RemoveImage(self, 'remove-image', '')

    # Test the alias of remove-image ('ri')
    def test_ri(self):
	RemoveImageTest.RemoveImage(self, 'ri', '')

    # Test the optional parameters '--force' and '-f'
    def test_remove_image_force(self):
	RemoveImageTest.RemoveImage(self, 'remove-image', '--force')
    def test_remove_image_f(self):
	RemoveImageTest.RemoveImage(self, 'remove-image', '-f')
	
    # Test the optional parameters '--owner' and '-o' 
    def test_remove_image_owner(self):
	(output, returncode) = self.run_repoman_command('whoami')
	RemoveImageTest.RemoveImage(self, 'remove-image', '--owner %s' % (output))
    def test_remove_image_o(self):
        (output, returncode) = self.run_repoman_command('whoami')
        RemoveImageTest.RemoveImage(self, 'remove-image', '-o %s' % (output))


#####################################################################
#               COMMAND - 'repoman share-image-with-groups'
#####################################################################


class ShareImageWithGroupsTest(RepomanCLITest):

    def ShareImageWithGroups(self, command, arg):
        """
        This method is called whenever the 'share-image-with-groups' or 'sig' command is used. The arguments are command and arg. 
        The argument 'command' can have the values 'share-image-with-groups' or 'sig'. arg contains optional parameters or is an empty sting if 
        there are none. Here the image is shared with the group 'users'.
        """
	# Use unique name for the image to be created
        self.new_image_name = self.get_unique_image_name()

	# Create the image to be shared by running the repoman create-image subcommand
        (output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
        self.assertEqual(returncode, 0)

	# Running the command ('share-image-with-groups' or 'sig'). The optional parameter '--owner' or '-o' can be passed in arg
	# The image is shared with the group 'users'
        (output, returncode) = self.run_repoman_command('%s %s users  %s' % (command, self.new_image_name, arg))
        p = re.search(r'OK.*Shared image: \'%s\' with group: \'users\'' % (self.new_image_name), output)
        self.assertTrue( p != None )
        self.assertEqual(returncode, 0)

	# Checking if the image shared is present in the 'repoman list-images --group' command
        (output, returncode) = self.run_repoman_command('list-images --group users')
        p = re.search(self.new_image_name, output)
        self.assertTrue( p != None )

    # Removing the image after the test
    def tearDown(self):
        (output, returncode) = self.run_repoman_command('remove-image --force %s' % (self.new_image_name))

    # Test the 'share-image-with-groups' subcommand
    def test_share_image_with_groups(self):
        ShareImageWithGroupsTest.ShareImageWithGroups(self, 'share-image-with-groups', '')

    # Test the alias 'sig'
    def test_sig(self):
        ShareImageWithGroupsTest.ShareImageWithGroups(self, 'sig', '')

    # Test the optional parameters '--owner' and '-o'. The current user is passed as the owner of the image
    def test_share_image_with_groups_owner(self):
	(output, returncode) = self.run_repoman_command('whoami')
	ShareImageWithGroupsTest.ShareImageWithGroups(self, 'share-image-with-groups', '--owner %s' % (output))
    def test_share_image_with_groups_o(self):
        (output, returncode) = self.run_repoman_command('whoami')
        ShareImageWithGroupsTest.ShareImageWithGroups(self, 'share-image-with-groups', '-o %s' % (output))



#####################################################################
#               COMMAND - 'repoman share-image-with-users'
#####################################################################


class ShareImageWithUsersTest(RepomanCLITest):

    def ShareImageWithUsers(self, command, arg):
	"""
	This method is called whenever the command 'share-image-with-users' or 'siu' is tested. The argument command can have
	the values 'share-image-with-users' or 'siu'. arg is for optional parameters. It is empty when there are none.
	An image with a unique name is shared with a new test user (created with a unique name). The output and status are checked.
	"""

	# Get unique names for the image and first and last names for the test user to be created
	self.new_image_name = self.get_unique_image_name()
	self.first_name = self.get_unique_image_name()
	self.last_name = self.get_unique_image_name()	
	
	# Create the test user. The first name is used for for the username and email address. The first and last names are used for the client DN and full name 
	(output, returncode) = self.run_repoman_command('create-user %s "/C=CA/O=Grid/OU=phys.UVic.CA/CN=%s %s" --email %s@random.com --full_name "%s %s"' % (self.first_name,self.first_name, self.last_name,self.first_name, self.first_name ,self.last_name))
	self.assertEqual(returncode, 0)

	# Create the image to be shared
	(output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
	self.assertEqual(returncode, 0)
	
	# Share the image with the test user and check the status and output
	(output, returncode) = self.run_repoman_command('%s %s %s %s' % (command, self.new_image_name,self.first_name, arg ))
	p = re.search(r"OK.*Shared image:\s*'%s' with user:\s*'%s'" % (self.new_image_name, self.first_name), output)
	self.assertTrue( p != None )
	self.assertEqual(returncode, 0)

	# Check if the image is listed with the shared images between the current user and the test user
	(output, returncode) = self.run_repoman_command('list-images -u %s' % (self.first_name))
	p = re.search(self.new_image_name, output)
	self.assertTrue (p != None)
	self.assertEqual(returncode, 0)


    def tearDown(self):
	"""
	This method removes the image and test user
	"""
	(output, returncode) = self.run_repoman_command('remove-image --force %s' % (self.new_image_name))
	(output, returncode) = self.run_repoman_command('remove-user --force %s' % (self.first_name))


    # Test the command 'share-image-with-users'
    def test_share_image_with_users(self):
	ShareImageWithUsersTest.ShareImageWithUsers(self, 'share-image-with-users', '')

    # Test the alias 'siu'
    def test_siu(self):
	ShareImageWithUsersTest.ShareImageWithUsers(self, 'siu', '')

    # Test the optional parameter '--owner' and '-o'. The current user is passed as the owner of the image
    def test_share_image_with_users_owner(self):
	(output, returncode) = self.run_repoman_command('whoami')
        ShareImageWithUsersTest.ShareImageWithUsers(self, 'share-image-with-users', '--owner %s' % (output))
    def test_share_image_with_users_o(self):
        (output, returncode) = self.run_repoman_command('whoami')
        ShareImageWithUsersTest.ShareImageWithUsers(self, 'share-image-with-users', '-o %s' % (output))


#####################################################################
#               COMMAND - 'repoman unshare-image-with-groups'
#####################################################################


class UnshareImageWithGroupsTest(RepomanCLITest):

    def UnshareImageWithGroups(self, command, arg):
	"""
	This method is called whenever the 'unshare-image-with-groups' or 'uig' command is tested. The arguments are command and arg. 
	The argument 'command' can have the values 'unshare-image-with-groups' or 'uig'. arg contains optional parameters or is an empty sting if 
	there are none. Here the image is shared and unshared with the group 'users'. 
	"""
	# Get a unique name for the image
	self.new_image_name = self.get_unique_image_name()
	
	# Create the image 
	(output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
	self.assertEqual(returncode, 0)
	
	# Share the image with the group 'users'
	(output, returncode) = self.run_repoman_command('share-image-with-groups %s users' % (self.new_image_name))
	self.assertEqual(returncode, 0)
	
	# Run the command 'unshare-image-with-groups' or 'uig' with optional parameters passed in arg
	# arg is an empty string if there are no optional parameters passed
	(output, returncode) = self.run_repoman_command('%s %s users  %s' % (command, self.new_image_name, arg))
	p = re.search(r'OK.*Unshared image: \'%s\' with group: \'users\'' % (self.new_image_name), output)
	self.assertTrue( p != None )
	self.assertEqual(returncode, 0)
        
	# Check the absence of the image in the shared images between the user and the group 'users'
	(output, returncode) = self.run_repoman_command('list-images --group users')
	p = re.search(self.new_image_name, output)
	self.assertTrue( p == None )

    # Remove the image that was created
    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-image --force %s' % (self.new_image_name))
	
    # Test the repoman subcommand 'unshare-image-with-groups'
    def test_unshare_image_with_groups(self):
	UnshareImageWithGroupsTest.UnshareImageWithGroups(self, 'unshare-image-with-groups', '')

    # Test the alias 'uig'
    def test_uig(self):
	UnshareImageWithGroupsTest.UnshareImageWithGroups(self, 'uig', '')


    # Test the optional parameters '--owner' and '-o'. The current user is passed as the owner of the image (same as default)
    def test_unshare_image_with_groups(self):
	(output, returncode) = self.run_repoman_command('whoami')
        UnshareImageWithGroupsTest.UnshareImageWithGroups(self, 'unshare-image-with-groups', '--owner %s' % (output))
    def test_unshare_image_with_groups_o(self):
        (output, returncode) = self.run_repoman_command('whoami')
        UnshareImageWithGroupsTest.UnshareImageWithGroups(self, 'unshare-image-with-groups', '-o %s' % (output))




#####################################################################
#               COMMAND - 'repoman unshare-image-with-users'
#####################################################################


class UnshareImageWithUsersTest(RepomanCLITest):

    def UnshareImageWithUsers(self, command, arg):
	"""
	This method is called whenever the 'unshare-image-with-users' or 'uiu' is tested. The argument command can 
	either have the value 'unshare-image-with-users' or 'uiu'. arg contains the optional parameters. It is an empty
	string when there are no optional parameters used. The image is shared with a test user, and then unshared.
	"""
	# Get unique names for the image and first and last names for the test user to be created
        self.new_image_name = self.get_unique_image_name()
        self.first_name = self.get_unique_image_name()
        self.last_name = self.get_unique_image_name()

        # Create the test user. The first name is used for for the username and email address. The first and last names are used for the client DN and full name 
        (output, returncode) = self.run_repoman_command('create-user %s "/C=CA/O=Grid/OU=phys.UVic.CA/CN=%s %s" --email %s@random.com --full_name "%s %s"' % (self.first_name,self.first_name, self.last_name,self.first_name, self.first_name ,self.last_name))
        self.assertEqual(returncode, 0)

        # Create the image to be shared
        (output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
        self.assertEqual(returncode, 0)

        # Share the image with the test user
        (output, returncode) = self.run_repoman_command('share-image-with-users %s %s' % (self.new_image_name,self.first_name))
        self.assertEqual(returncode, 0)

	# Unshare the image and test the status and output
	(output, returncode) = self.run_repoman_command('%s %s %s %s' % (command, self.new_image_name, self.first_name, arg))
	p = re.search(r"OK.*Unshared image:\s*'%s' with user:\s*'%s'" % (self.new_image_name, self.first_name), output)
	self.assertTrue( p != None )
	self.assertEqual(returncode, 0)

        # Check if the image is not listed with the shared images between the current user and the test user
        (output, returncode) = self.run_repoman_command('list-images -u %s' % (self.first_name))
        p = re.search(self.new_image_name, output)
        self.assertTrue (p == None)
        self.assertEqual(returncode, 0)


    def tearDown(self):
        """
        This method removes the image and test user
        """
        (output, returncode) = self.run_repoman_command('remove-image --force %s' % (self.new_image_name))
        (output, returncode) = self.run_repoman_command('remove-user --force %s' % (self.first_name))


    # This tests the command 'unshare-image-with-users'
    def test_unshare_image_with_users(self):
        UnshareImageWithUsersTest.UnshareImageWithUsers(self, 'unshare-image-with-users', '')

    #This tests the alias 'uiu'
    def test_uiu(self):
        UnshareImageWithUsersTest.UnshareImageWithUsers(self, 'uiu', '')

    # Test the optional parameters '--owner' and '-o'. The current user is passed as the owner of the image
    def test_unshare_image_with_users_owner(self):
	(output, returncode) = self.run_repoman_command('whoami')
        UnshareImageWithUsersTest.UnshareImageWithUsers(self, 'unshare-image-with-users', '--owner %s' % (output))
    def test_unshare_image_with_users_o(self):
        (output, returncode) = self.run_repoman_command('whoami')
        UnshareImageWithUsersTest.UnshareImageWithUsers(self, 'unshare-image-with-users', '-o %s' % (output))



#***********************************************************************************************#
#				USER MANUPILATION SUBCOMMANDS					#
#***********************************************************************************************#




#####################################################################
#               COMMAND - 'repoman create-user'
#####################################################################


class CreateUserTest(RepomanCLITest):

    def CreateUser(self, command, arg):
	"""
	This method is used whenever the create-user or cu subcommand is tested. The argument 'command'
	stores the command 'create-user' or its alias 'cu'. The argument arg stores any optional parameters.
	If passed without optional parameters, arg is an empty string.
	"""
	# Get a unique name for the first and last names of the user to be created
	self.first_name = self.get_unique_image_name()
	self.last_name = self.get_unique_image_name()
	
	# If the optional parameters '--email' or '-e is chosen, add a random email address with the first name and domain name 'random.com'
	if (arg == '--email' or arg == '-e'):
		arg = arg + ' ' + self.first_name + '@random.com'
	# If the optional parameters '--full' or '-f' is chosen, add the first and last names
	elif (arg == '--full_name' or arg == '-f'):
		arg = arg + ' "%s %s"' % (self.first_name, self.last_name)
	
	# Run the repoman command for creating the user 
	(output, returncode) = self.run_repoman_command('%s %s "/C=CA/O=Grid/OU=phys.UVic.CA/CN=%s %s" %s' % (command, self.first_name,self.first_name, self.last_name, arg))
	p = re.search(r'OK.*Created new user %s' % (self.first_name), output)
	self.assertEqual(returncode, 0)
	self.assertTrue(p != None)
	# Check if the user is listed in 'repoman list-users'
	(output, returncode) = self.run_repoman_command('list-users')
	p = re.search(self.first_name, output)
	self.assertTrue(p != None)

	# If the email address or full name is specified, the address/full name is checked in the description of the user
	if (re.search('-e',arg)):
		(output, returncode) = self.run_repoman_command('list-users %s' % (self.first_name))
		p = re.search(r'email : %s@random.com' % (self.first_name), output)
		self.assertTrue(p != None)
	elif (re.search('-f', arg)):
		(output, returncode) = self.run_repoman_command('list-users %s' % (self.first_name))
                p = re.search(r'full_name : %s %s' % (self.first_name, self.last_name), output)
                self.assertTrue(p != None)

    # Remove the user that was created at the end of the test	
    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-user --force %s' % (self.first_name))

    # Test the command without optional parameters
    def test_create_user(self):
	CreateUserTest.CreateUser(self, 'create-user', '')

    # Test the alias of the command (without optional parameters)
    def test_cu(self):
	CreateUserTest.CreateUser(self, 'cu', '')

    # Test the optional parameters '--email' or '-e'
    def test_create_user_email(self):
	CreateUserTest.CreateUser(self, 'create-user', '--email')
    def test_create_user_e(self):
        CreateUserTest.CreateUser(self, 'create-user', '-e')

    # Test the optional parameters '--full_name' or '-f'
    def test_create_user_full_name(self):
	CreateUserTest.CreateUser(self, 'create-user', '--full_name')
    def test_create_user_f(self):
	CreateUserTest.CreateUser(self, 'create-user', '-f')




#####################################################################
#               COMMAND - 'repoman list-users'
#####################################################################


class ListUsersTest(RepomanCLITest):

    def ListUsers(self, command, arg):
	"""
	This method is used whenever the 'list-users' or 'lu' command is used. The argument command has the value 'list-users' or 'lu'. 
	arg contains any optional parameter. Here the output of the list-images is checked to match the expected value
	"""
	# Get a unique name for the first name and last name for the test user
	self.first_name = self.get_unique_image_name()
	self.last_name = self.get_unique_image_name()
	
	# Create a test user. The first name is used for the username and email address. The last name is used in the DN and full_name fields
	(output, returncode) = self.run_repoman_command('create-user %s "/C=CA/O=Grid/OU=phys.UVic.CA/CN=%s %s" --email %s@random.com --full_name "%s %s"' % (self.first_name,self.first_name, self.last_name,self.first_name, self.first_name ,self.last_name))
        self.assertEqual(returncode, 0)

	# Test the 'list-user' or 'lu' command with or without optional parameters
	(output, statuscode) = self.run_repoman_command('%s %s' % (command,arg ))
	p = re.search(self.first_name, output)
	self.assertTrue(p != None)
	self.assertEqual(returncode, 0)
	
	# Test the optional parameter '-l' or '--long'
	if (arg == '-l' or arg == '--long'):
		p = re.search(r'Username\s*Full Name\s*Client DN', output)
		self.assertTrue(p != None)

    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-user --force %s' % (self.first_name))

    # Test the command 'list-users' without parameters. arg is passed as empty string	
    def test_list_users(self):
	ListUsersTest.ListUsers(self, 'list-users', '')

    # Test the alias 'lu'
    def test_lu(self):
	ListUsersTest.ListUsers(self, 'lu', '')

    # Test the optional parameters '-l' and '--long'
    def test_list_users_long(self):
	ListUsersTest.ListUsers(self, 'list-users', '--long')	
    def test_list_users_l(self):
	ListUsersTest.ListUsers(self, 'list-users', '-l')

    # Test the optional parameters '--group' and '-g'. Here the user is checked in the default group 'users'
    def test_list_users_group(self):
	ListUsersTest.ListUsers(self, 'list-users', '--group users')
    def test_list_users_group(self):
	ListUsersTest.ListUsers(self, 'list-users', '-g users')


    def test_list_users_user(self):
	# Get a unique name for the first name and last name for the test user
        self.first_name = self.get_unique_image_name()
        self.last_name = self.get_unique_image_name()

        # Create a test user. The first name is used for the username and email address. The last name is used in the DN and full_name fields
        (output, returncode) = self.run_repoman_command('create-user %s "/C=CA/O=Grid/OU=phys.UVic.CA/CN=%s %s" --email %s@random.com --full_name "%s %s"' % (self.first_name,self.first_name, self.last_name,self.first_name, self.first_name ,self.last_name))
        self.assertEqual(returncode, 0)

        # Test the 'list-user user' command. The expected fields are checked.  
        (output, statuscode) = self.run_repoman_command('list-users %s' % (self.first_name))
        p = re.search(r'client_dn :\s*/C=CA/O=Grid/OU=phys.UVic.CA/CN=%s %s\s*\n\s*email : %s@random.com\s*\n\s*full_name : %s %s\s*\n\s*groups :.*\n\s*images :.*\n\s*permissions :.*\n\s*suspended :.*\n\s*user_name :' % (self.first_name, self.last_name, self.first_name, self.first_name, self.last_name), output)
        self.assertTrue(p != None)
        self.assertEqual(returncode, 0)
    
	



#####################################################################
#               COMMAND - 'repoman modify-user'
#####################################################################


class ModifyUserTest(RepomanCLITest):

    def ModifyUser(self, command, arg):
	"""
	This method is called whenever the 'modify-user' or 'mu' command is used. The argument 'command' 
	stores 'modify-user' or 'mu'. Any optional parameter is stored in the argument 'arg'. 
	"""
	
	# Get unique names for the first and last names of the test user
	self.first_name = self.get_unique_image_name()
	self.last_name = self.get_unique_image_name()
	
	# Create a test user. The first name is used for the username and email address. The last name is used in the DN and full_name fields
        (output, returncode) = self.run_repoman_command('create-user %s "/C=CA/O=Grid/OU=phys.UVic.CA/CN=%s %s" --email %s@random.com --full_name "%s %s"' % (self.first_name,self.first_name, self.last_name,self.first_name, self.first_name ,self.last_name))
        self.assertEqual(returncode, 0)
	
	# Adding a unique random name to the optional parameters '--client_dn'/'-c', '--email'/'-e', '--full_name'/'-f' or '--new_user'/'-n'
	# The variable self.new_random_name will serve as the new client dn, email address, full name or new user to which the value will be modified to.
	if (arg != ''):
		self.new_random_name = self.get_unique_image_name()
		arg = arg + ' ' + self.new_random_name
		if (re.search('--email', arg) or re.search('-e', arg)):
			arg = arg + '@random.com'
	
	# Run the 'modify-image' or 'mu' command with or without optional parameters
	(output, statuscode) = self.run_repoman_command('%s %s %s' % (command, self.first_name, arg))
	p = re.search(r'OK.*Modifying user.', output)
	self.assertTrue(p != None)
	self.assertEqual(returncode, 0)

	if (arg != ''):
		(output, returncode) = self.run_repoman_command('list-users %s' % (self.first_name))
		self.assertEqual(returncode, 0)
		if (arg == '-c %s' % (self.new_random_name) or arg == '--client_dn %s' % (self.new_random_name)):
			p = re.search(r'client_dn : %s' % (self.new_random_name), output)
			self.assertTrue(p != None)
			self.assertEqual(returncode, 0)
		if (arg == 'e %s' % (self.new_random_name) or arg == '--email %s' % (self.new_random_name)):
			p = re.search(r'email : %s' % (self.new_random_name), output)
                        self.assertTrue(p != None)
                        self.assertEqual(returncode, 0)
		if (arg == '--full_name %s' % (self.new_random_name) or arg == '-f %s' % (self.new_random_name)):
			p = re.search(r'full_name : %s' % (self.new_random_name), output)
                        self.assertTrue(p != None)
                        self.assertEqual(returncode, 0)
		if (arg == '--new_name %s' % (self.new_random_name) or arg == '-n %s' % (self.new_random_name)):
			p = re.search(r'user_name : %s' % (self.new_random_name), output)
			self.assertTrue(p != None)
			self.assertEqual(returncode, 0)		


    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-user --force %s' % (self.first_name))

    def test_modify_user(self):
	ModifyUserTest.ModifyUser(self, 'modify-user', '')

    def test_mu(self):
	ModifyUserTest.ModifyUser(self, 'mu', '')

    # This tests the optional parameters '--client_dn' and '-c'. A unique name is assigned to the client dn.
    def test_modify_user_client_dn(self):
	ModifyUserTest.ModifyUser(self, 'modify-user', '--client_dn') 
    def test_modify_user_c(self):
	ModifyUserTest.ModifyUser(self, 'modify-user', '-c')

    # This tests the optional parameters '--email' and '-e'. The value for email address is a unique name assigned in the called method.
    def test_modify_user_email(self):
	ModifyUserTest.ModifyUser(self, 'modify-user', '--email')
    def test_modify_user_e(self):
	ModifyUserTest.ModifyUser(self, 'modify-user', '-e')

    # This tests the optional parameters '--full_name' and '-f'. The value for full name is given a unique name.
    def test_modify_user_full_name(self):
	ModifyUserTest.ModifyUser(self, 'modify-user', '--full_name')
    def test_modify_user_f(self):
	ModifyUserTest.ModifyUser(self, 'modify-user', '-f')

    # This tests the optional parameters '--new_name' and '-n'. The value is given a unique name assigned in the ModifyUser method.
#    def test_modify_user_new_name(self):
#	ModifyUserTest.ModifyUser(self, 'modify-user', '--new_name')
#    def test_modify_user_n(self):
#	ModifyUserTest.ModifyUser(self, 'modify-user', '-n')




#####################################################################
#		COMMMAND - 'repoman remove-user'
#####################################################################


class RemoveUserTest(RepomanCLITest):


    def RemoveUser(self, command, arg):
	"""
	This method is called whenever the 'remove-user' or 'ru' command is used. 
	The argument 'command' stores either 'remove-user' or 'ru'. 'arg' stores the optional parameters '--force' or '-f'
	Here a test user is created and removed. The successfull removal is checked with the command 'list-users'
	"""
	# Get a unique name for the first and last names of the test user
	self.first_name = self.get_unique_image_name()
	self.last_name = self.get_unique_image_name()
	
	# Create the test user. The first name is used for the username and email address. The last name is used in the client dn and full name.
	(output, returncode) = self.run_repoman_command('create-user %s "/C=CA/O=Grid/OU=phys.UVic.CA/CN=%s %s" --email %s@random.com --full_name "%s %s"' % (self.first_name,self.first_name, self.last_name,self.first_name, self.first_name ,self.last_name))
	self.assertEqual(returncode, 0)
	
	if (arg == ''):
		# Run the 'remove-user' or 'ru' command. The 'yes yes' is used to pass 'yes' to the confirmation prompt
        	# Here the function run_repoman_command is not used since 'yes yes |' has to precede 'repoman'.
        	p = Popen('yes yes | repoman %s %s' % (command, self.first_name), shell=True, stdout=PIPE, stderr=STDOUT)
        	output = p.communicate()[0]
        	m = re.search(r'OK.*Removed user', output)
        	self.assertTrue( m != None)
        	self.assertEqual(p.returncode, 0)
    
	elif (arg == '--force' or arg == '-f'):
		# Remove the user forcefully
        	(output, returncode) = self.run_repoman_command('remove-user %s %s' % (self.first_name, arg))
        	m = re.search(r'OK.*Removed user', output)
        	self.assertTrue( m != None)
	        self.assertEqual(returncode, 0)

	# Check the absence of the user in 'list-users'
	(output, returncode) = self.run_repoman_command('list-users')
	p = re.search(self.first_name, output)
	self.assertTrue(p == None)


    # Test the command 'remove-user'
    def test_remove_user(self):
	RemoveUserTest.RemoveUser(self, 'remove-user', '')

    # Test the alias 'ru'
    def test_ru(self):
	RemoveUserTest.RemoveUser(self, 'ru', '')

    # Test the optional parameter '--force' and '-f'
    def test_remove_user_force(self):
	RemoveUserTest.RemoveUser(self, 'remove-user', '--force')
    def test_remove_user_f(self):
        RemoveUserTest.RemoveUser(self, 'remove-user', '-f')





#***********************************************************************************************#
#                               GROUP MANUPILATION SUBCOMMANDS                                  #
#***********************************************************************************************#



#####################################################################
#               COMMAND - 'repoman add-permissions-to-group'
#####################################################################


class AddPermissionsToGroupTest(RepomanCLITest):

    def AddPermissionsToGroup(self, command):
	"""
	This method is called whenever the 'add-permissions-to-groups' or 'apg' commands are tested. 
	Here a group is created with a unique name and without any permissions. All the possible permissions
	are added using the command and the output and status are checked. The presence of the permissions 
	are also checked in the description of the group.
	"""
	# Generate a unique name for the new group 
	self.new_group_name = self.get_unique_image_name()
	# Create a new group without any permissions
	(output, returncode) = self.run_repoman_command('create-group %s' % (self.new_group_name))
	self.assertEqual(returncode, 0)
	
	# Add all possible permissions using the command 'add-permissions-to-groups' or 'apg'
	(output, returncode) = self.run_repoman_command('%s %s group_create,group_delete,group_modify,group_modify_membership,group_modify_permissions,image_create,image_delete,image_delete_group,image_modify,image_modify_group,user_create,user_delete,user_modify,user_modify_self' % (command, self.new_group_name)) 
	p = re.findall(r'OK.*Adding permission:', output)	
	self.assertEqual(len(p), 14)
	self.assertEqual(returncode, 0)

	# Check if the permissions show in the description of the group
	(output, returncode) = self.run_repoman_command('list-groups %s' % (self.new_group_name))
	p = re.search(r'permissions : group_create, group_delete, group_modify, group_modify_membership, group_modify_permissions, image_create, image_delete, image_delete_group, image_modify, image_modify_group, user_create, user_delete, user_modify, user_modify_self', output)
	self.assertTrue(p != None)
	self.assertEqual(returncode, 0)


    # Remove the group after the end of the test
    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-group %s --force' % (self.new_group_name))

    # Test the command 'add-permissions-to-group' 
    def test_add_permissions_to_group(self):
	AddPermissionsToGroupTest.AddPermissionsToGroup(self, 'add-permissions-to-group')

    # Test the alias 'apg'
    def test_apg(self):
	AddPermissionsToGroupTest.AddPermissionsToGroup(self, 'apg')





#####################################################################
#               COMMAND - 'repoman add-users-to-group'
#####################################################################


class AddUsersToGroupTest(RepomanCLITest):

    def AddUsersToGroup(self, command):
	"""
	This method is used whenever the 'add-users-to-group' or 'aug' subcommand is tested. The command or its alias
	is passed into the argument 'command'. Here a group is created without any permissions or members. Then the command
	is used to add the current user to the group. The status and output is checked. The presence of the user is also checked
	in the description of the group.
	"""
	# Get a unique name for the group and create the group without permissions or users
	self.new_group_name = self.get_unique_image_name()
	(output, returncode) = self.run_repoman_command('create-group %s' % (self.new_group_name))
	self.assertEqual(returncode, 0)
	# Get the username of the current user and store it in the variable 'user'
	(user, status) = self.run_repoman_command('whoami')
	
	# Run the 'add-users-to-group' or 'aug' command
	(output, returncode) = self.run_repoman_command('%s %s %s' % (command, self.new_group_name, user))
	p = re.search(r'OK.*Adding user:', output)
	self.assertTrue(p != None)
	self.assertEqual(returncode, 0)
	
	# Check the presence of the current user in the description of the group 
	(output, returncode) = self.run_repoman_command('list-groups %s' % (self.new_group_name))
	p = re.search(r'users :.*%s' % (user), output)
	self.assertTrue(p != None)
	self.assertEqual(returncode, 0)
	
    # Remove the group after test completes
    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-group --force %s' % (self.new_group_name))
	

    # Test the command 'add-users-to-group'
    def test_add_user_to_group(self):
	AddUsersToGroupTest.AddUsersToGroup(self, 'add-users-to-group')

    # Test the alias 'aug'
    def test_aug(self):
	AddUsersToGroupTest.AddUsersToGroup(self, 'aug')
	
	



#####################################################################
#               COMMAND - 'repoman create-group'
#####################################################################


class CreateGroupTest(RepomanCLITest):

    def CreateGroup(self, command, arg):
	"""
	This method is called whenever the 'create-group' or 'cg' command is tested. The command or its alias is stored in the 
	argument 'command' and optional parameters are stored in the argument 'arg'. 
	"""
	# Generate a unique name for the new group
	self.new_group_name = self.get_unique_image_name()
	
	# Run the subcommand and check the output and status
	(output, returncode) = self.run_repoman_command('%s %s %s' % (command, self.new_group_name, arg))
	p = re.search(r"OK.*Creating new group: '%s'" % (self.new_group_name), output)
	self.assertTrue(p != None)
	self.assertEqual(returncode, 0)

	# Check if the group can be listed
	(output, returncode) = self.run_repoman_command('list-groups %s' % (self.new_group_name))
	p = re.search(r'name : %s' % (self.new_group_name), output)
	self.assertTrue(p != None)
	
	# Check the changes due to the optional parameters
	if (re.search('-p',arg)):
		p = re.search(r'permissions : group_create, group_delete, group_modify, group_modify_membership, group_modify_permissions, image_create, image_delete, image_delete_group, image_modify, image_modify_group, user_create, user_delete, user_modify, user_modify_self', output)
        	self.assertTrue(p != None)
	if (re.search('-u', arg)):
		(user, status) = self.run_repoman_command('whoami')
		p = re.search(r'users :.*%s' % (user), output)
                self.assertTrue(p != None)
		
    # Remove the group after the tests
    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-group --force %s' % (self.new_group_name))

    # Test the command 'create-group' without optional parameters
    def test_create_group(self):
	CreateGroupTest.CreateGroup(self, 'create-group', '')

    # Test the alias 'cu' without optional parameters
    def test_cg(self):
	CreateGroupTest.CreateGroup(self, 'cg', '')

    # Test the optional parameters '--permissions' or '-p'. Here all the possible permissions are given to the group
    def test_create_group_permissions(self):
	CreateGroupTest.CreateGroup(self, 'create-group', '--permissions group_create,group_delete,group_modify,group_modify_membership,group_modify_permissions,image_create,image_delete,image_delete_group,image_modify,image_modify_group,user_create,user_delete,user_modify,user_modify_self')
    def test_create_group_p(self):
	CreateGroupTest.CreateGroup(self, 'create-group', '-p group_create,group_delete,group_modify,group_modify_membership,group_modify_permissions,image_create,image_delete,image_delete_group,image_modify,image_modify_group,user_create,user_delete,user_modify,user_modify_self')	

    # Test the optional parameters '--users' and '-u'. Here the current user is passed as the user of the group
    def test_create_group_users(self):
	(output, returncode) = self.run_repoman_command('whoami')
	CreateGroupTest.CreateGroup(self, 'create-group', '--users %s' % (output))
    def test_create_group_u(self):
	(output, returncode) = self.run_repoman_command('whoami')
        CreateGroupTest.CreateGroup(self, 'create-group', '-u %s' % (output))



#####################################################################
#               COMMAND - 'repoman list-groups'
#####################################################################


class ListGroupsTest(RepomanCLITest):

    def ListGroups(self, command, arg):
	"""
	This method is called whenever the 'list-groups' or 'lg' subcommands are tested. The argument command
	stores the 'list-groups' or 'lg'. arg stores the optional parameters (is an empty string if no optional parameters are passed)
	"""
	# Generate a unique name for the new group to be created
	self.new_group_name = self.get_unique_image_name()
	# Create a group with the unique name and make the current user a group member
	(user, status) = self.run_repoman_command('whoami')
	(output, returncode) = self.run_repoman_command('create-group %s --users %s' % (self.new_group_name, user))  
	self.assertEqual(returncode, 0)
	
	# For the optional parameter 'group', the name of the new group is assigned to arg
	if (arg == 'group'):
		arg = self.new_group_name
	# For the optional parameter '--user' or '-u', the current user is added as a memeber  
	if (re.search('-u', arg)):
		arg = arg + ' ' + user
	# Run the command for listing the groups (with or without the optional parameters)
	(output, returncode) = self.run_repoman_command('%s %s' % (command, arg))
	p = re.search(self.new_group_name, output)
	self.assertTrue(p != None)
	self.assertEqual(returncode, 0)

	# Check if the decription of the group is outputted if the 'group' optional parameter is chosen
	if (arg == self.new_group_name):
		p = re.search(r'name :.*\n\s*permissions :.*\n\s*users :', output)
		self.assertTrue(p != None)
		self.assertEqual(returncode, 0)
	# Check the fields if the '--long' or '-l' optional parameters are chosen
	if (arg == '--long' or arg == '-l'):
		p = re.search(r'Group Name\s*Members', output)	
		self.assertTrue(p != None)
		self.assertEqual(returncode, 0)

    # Remove the group after the test completes
    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-group --force %s' % (self.new_group_name))

    # Test the command 'list-groups' without optional parameters
    def test_list_groups(self):
	ListGroupsTest.ListGroups(self, 'list-groups', '')

    # Test the alias 'lg' without optional parameters
    def test_lg(self):
	ListGroupsTest.ListGroups(self, 'lg', '')



	#########################################################
        #               OPTIONAL PARAMETERS                     #       
        #########################################################



    # Test the optional parameters '--all' and '-a'
    def test_list_groups_all(self):
	ListGroupsTest.ListGroups(self, 'list-groups', '--all')
    def test_list_groups_a(self):
	ListGroupsTest.ListGroups(self, 'list-groups', '-a')

    # Test the optional parameter 'group'. The name of the group is generated and assigned in the ListGroups method
    def test_list_groups_group(self):
	ListGroupsTest.ListGroups(self, 'list-groups', 'group')

    # Test the optional parameters '--long' and '-l'
    def test_list_groups_long(self):
	ListGroupsTest.ListGroups(self, 'list-groups', '--long')
    def test_list_groups_l(self):
	ListGroupsTest.ListGroups(self, 'list-groups', '-l')

    # Test the optional parameters '--user' and '-u'. The current user is chosen as the user
    def test_list_groups_user(self):
	ListGroupsTest.ListGroups(self, 'list-groups', '--user')
    def test_list_groups_u(self):
	ListGroupsTest.ListGroups(self, 'list-groups', '-u')





#####################################################################
#               COMMAND - 'repoman modify-group'
#####################################################################


#class ModifyGroupTest(RepomanCLITest):

#    def ModifyGroup(self, command, arg):
#	"""
#	This method is called whenever the 'modify-group' or 'mg' command is used.
#	The argument command stores either 'modify-group' or 'mg' while arg stores the optional parameters.
#	"""


#####################################################################
#               COMMAND - 'repoman remove-group'
#####################################################################


class RemoveGroupTest(RepomanCLITest):

    def RemoveGroup(self, command, arg):
	"""
	This method is called whenever the 'remove-group' or 'rg' command is used. The argument command
	stores the command or its alias, while arg stores the optional parameters. Here a group is first created 
	with a unique name, it is removed by running the command and its absence is checked in the command
	'repoman list-groups --all'.
	"""
	# Generate a unique name for the group and create a group
	self.new_group_name = self.get_unique_image_name()
	(output, returncode) = self.run_repoman_command('create-group %s' % (self.new_group_name))
	self.assertEqual(returncode, 0)

	# If the command is passed without optional parameters, use the 'yes yes' command to automatically agree
	# to the confirmation prompt for removing the group
	# Here the function run_repoman_command is not used since 'yes yes |' has to precede 'repoman'.
        if (arg == ''):
	        p = Popen('yes yes | repoman %s %s' % (command, self.new_group_name), shell=True, stdout=PIPE, stderr=STDOUT)
                output = p.communicate()[0]
                m = re.search(r'OK.*Removed group %s' % (self.new_group_name), output)
                self.assertTrue( m != None)
                self.assertEqual(p.returncode, 0)
	# When the '--force' or '-f' optional parameter is used, it is run using 'run_repoman_command'
        elif (arg == '--force' or arg == '-f'):
                # Remove the group forcefully
                (output, returncode) = self.run_repoman_command('%s %s %s' % (command, self.new_group_name, arg))
                m = re.search(r'OK.*Removed group %s' % (self.new_group_name), output)
                self.assertTrue( m != None)
                self.assertEqual(returncode, 0)
	
	# Check the absence of the group in 'repoman list-groups --all'
	(output, returncode) = self.run_repoman_command('list-groups --all')
	p = re.search(self.new_group_name, output)
	self.assertTrue(p == None)
	
    # Test the command 'remove-group' without optional parameters
    def test_remove_group(self):
	RemoveGroupTest.RemoveGroup(self, 'remove-group', '')

    # Test the alias without optional parameters
    def test_rg(self):
	RemoveGroupTest.RemoveGroup(self, 'rg', '')

    # Test the optional parameters '--force' and '-f'
    def test_remove_group_force(self):
	RemoveGroupTest.RemoveGroup(self, 'remove-group', '--force')
    def test_remove_group_f(self):
	RemoveGroupTest.RemoveGroup(self, 'remove-group', '-f')


	


#####################################################################
#	COMMAND - 'repoman remove-permissions-from-group'
#####################################################################


class RemovePermissionsFromGroupTest(RepomanCLITest):

    def RemovePermissionsFromGroup(self, command):
	"""
	This method is used whenever the 'remove-permissions-from-group' or 'rpg' command is used. The command
	or its alias is stored in the argument 'command'. Here a group is created with a unique name and with
	all possible permissions. All the permissions are then removed using the command to be tested or its 
	alias. The status and output are checked. The absence of the permissions is also checked in the description
	of the group.
	"""
	# Generate a unique name for the group
	self.new_group_name = self.get_unique_image_name()
	# Create group with unique name and all possible permissions
	(output, returncode) = self.run_repoman_command('create-group %s --permissions group_create,group_delete,group_modify,group_modify_membership,group_modify_permissions,image_create,image_delete,image_delete_group,image_modify,image_modify_group,user_create,user_delete,user_modify,user_modify_self' % (self.new_group_name))
	self.assertEqual(returncode, 0)
	
	# Remove the permissions using the command or its alias
	(output, returncode) = self.run_repoman_command('%s %s group_create,group_delete,group_modify,group_modify_membership,group_modify_permissions,image_create,image_delete,image_delete_group,image_modify,image_modify_group,user_create,user_delete,user_modify,user_modify_self' % (command, self.new_group_name))
	p = re.findall(r'OK.*Removing permission:', output)
	self.assertEqual(len(p), 14)
	self.assertEqual(returncode, 0)

	# Check the absence of the permissions in the description of the group
	(output, returncode) = self.run_repoman_command('list-groups %s' % (self.new_group_name))
	p = re.search(r'permissions :\s*\n\s*users :', output)
	self.assertTrue(p != None)
	self.assertEqual(returncode, 0)

    # Remove the group after the test completes
    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-group --force %s' % (self.new_group_name))

    # Test the command 'remove-permissions-from-group'
    def test_remove_permissions_from_group(self):
	RemovePermissionsFromGroupTest.RemovePermissionsFromGroup(self, 'remove-permissions-from-group')

    # Test the alias 'rpg'
    def test_rpg(self):
        RemovePermissionsFromGroupTest.RemovePermissionsFromGroup(self, 'rpg')




#####################################################################
#       	COMMAND - 'repoman remove-users-from-group'
#####################################################################


class RemoveUsersFromGroupTest(RepomanCLITest):

    def RemoveUsersFromGroup(self, command):
	"""
	This method is used whenever the command 'remove-users-from-group' or its alias 'rug' is used. The command 
	or its alias is stored in the argument 'command'. Here a unique name for the group is first generated. The
	group is created using the unique name and with the current user as one of its members. The user is then 
	removed using the command to be tested or its alias. The status and output are checked. The absence of the
	user is also checked in the description of the group.
	"""
	# Generate a unique name for the group
	self.new_group_name = self.get_unique_image_name()
	# Create the group with the current user as a group member.
	# The current user is stored in 'user'
	(user, status) = self.run_repoman_command('whoami')
	(output, returncode) = self.run_repoman_command('create-group %s --users %s' % (self.new_group_name, user))
	self.assertEqual(returncode, 0)

	# Remove the current user from the group using the command to be tested or the alias
	(output, returncode) = self.run_repoman_command('%s %s %s' % (command, self.new_group_name, user))
	p = re.search(r'OK.*Removing user:', output)
	self.assertTrue(p != None)
	self.assertEqual(returncode, 0)

	# Check the absence of the user in the description of the group
	(output, returncode) = self.run_repoman_command('list-groups %s' % (self.new_group_name))
	p = re.search(user, output)
	self.assertTrue(p == None)
	self.assertEqual(returncode, 0)
	
    # Remove the group after the completion of the test
    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-group --force %s' % (self.new_group_name))

    # Test the command 'remove-users-from-group'
    def test_remove_users_from_group(self):
	RemoveUsersFromGroupTest.RemoveUsersFromGroup(self, 'remove-users-from-group')

    # Test the alias 'rug'
    def test_rug(self):
	RemoveUsersFromGroupTest.RemoveUsersFromGroup(self, 'rug')


 

#####################################################################
#####################################################################
#####################################################################




#
# The entrypoint into the script.
# No need to modify this at this point.
#

if __name__ == '__main__':
    unittest.main()

