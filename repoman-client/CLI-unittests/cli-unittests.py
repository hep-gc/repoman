import re
import sys
import uuid
import unittest
from subprocess import Popen, PIPE, STDOUT


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
#            print 'Running [%s]' % (cmd)
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
        self.assertEqual(output, '0.3.11\n')
        self.assertEqual(returncode, 0)


######################################################################
#		COMMAND - 'repoman whoami'
######################################################################


class WhoamiTest(RepomanCLITest):
    def test_whoami(self):
        (output, returncode) = self.run_repoman_command('whoami')
        self.assertEqual(returncode, 0)


######################################################################


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


    def test_create_image_file(self):
	CreateImageTest.CreateImageFile(self, '--file')

    def test_create_image_f(self):
	CreateImageTest.CreateImageFile(self, '-f')



		
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
	# Run 'repoman modify-image' and check the output
	(output, returncode) = self.run_repoman_command('modify-image %s %s' %(self.new_image_name, arg))
	self.assertEqual(output, "[OK]     Modifying image.\n")
	self.assertEqual(returncode, 0)
	
	if (arg == '--new_name %s' % (random_name) or arg == '-n %s' % (random_name)):
		(output, returncode) = self.run_repoman_command('list-images %s' % (random_name))
		p = re.search('^\\s*name : %s\\s*$' % (random_name), output, flags=re.MULTILINE)
                self.assertTrue(p != None)
		
		
		
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
    def test_modify_image_new_name(self, tearDown = None):
	ModifyImageTest.ModifyImage(self, '--new_name ')
    def test_modify_image_n(self):
	ModifyImageTest.ModifyImage(self, '-n ')		

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
		p = re.search(r'\s*Image\s*Name\s*Owner\s*Size\s*Last Modified\s*Description', output)
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
	The test is successful if the shared image is listed with the command 'list-images --group users' or 'list-users -g users'
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


    # Test the optional parameter 'image'
    def test_list_images_image(self):
	"""
	This test runs the 'repoman list-images image' command, and checks if all the fields of the output match the expected fields of the image
	"""
	self.new_image_name = self.get_unique_image_name()
        (output, returncode) = self.run_repoman_command("create-image %s" % (self.new_image_name))
        self.assertEqual(returncode, 0)

	# Check if the output is of the proper format
	(output, returncode) = self.run_repoman_command("list-images %s" % (self.new_image_name))
	p = re.search(r'checksum :.*\n\s*description :.*\n\s*expires :.*\n\s*file_url :.*\n\s*http_file_url :.*\n\s*hypervisor :.*\n\s*modified :.*\n\s*name : %s.*\n\s*os_arch :.*\n\s*os_type :.*\n\s*os_variant :.*\n\s*owner :.*\n\s*owner_user_name :.*\n\s*raw_file_uploaded :.*\n\s*read_only :.*\n\s*shared_with :.*\n\s*size :.*\n\s*unauthenticated_access :.*\n\s*uploaded :.*\n\s*uuid :.*\n\s*version :' % (self.new_image_name), output)
	self.assertTrue( p != None)
        self.assertEqual(returncode, 0)




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

        # Upload the file with the 'put-image' or 'pi' command into the newly created image
        (output, returncode) = self.run_repoman_command('%s %s %s' % (command,random_file, self.new_image_name ))
        p = re.search(r'Uploading %s to image.+\n.*OK.*%s uploaded to image' % (random_file, random_file), output)
	self.assertTrue( p != None)
	self.assertEqual(returncode, 0)

	if (arg == ''):
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

        	# Check if the file that got uploaded and consequently downloaded matches the original file
        	p = Popen('diff %s %s' % (random_file, self.new_image_name), shell=True, stdout=PIPE, stderr=STDOUT)
        	output = p.communicate()[0]
        	self.assertEqual(p.returncode, 0)

        	# Delete the dummy file (random_file) and the downloaded file
        	p = Popen('rm %s %s' % (random_file, self.new_image_name), shell=True, stdout=PIPE, stderr=STDOUT)
        	output = p.communicate()[0]
        	self.assertEqual(p.returncode, 0)
	
	elif (arg == '--force'):
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
                p = Popen('wget %s' % (m[0]), shell=True, stdout=PIPE, stderr=STDOUT)
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

    # Test the optional parameter, '--force'
    def test_put_image_force(self):
	PutImageTest.PutImage(self, 'put-image', '--force')

    def tearDown(self):
	(output, returncode) = self.run_repoman_command('remove-image -f %s' %(self.new_image_name))	




#####################################################################
#               COMMAND - 'repoman remove-image'
#####################################################################


class RemoveImageTest(RepomanCLITest):

    def RemoveImage(self, command, arg):
	"""
	This method is called whenever the commands 'remove-image' or 'ri' is used. The arguments are command and arg. 
	The argument 'command' can have the value 'remove-image' or 'ri', while 'arg' contains the optional parameters
	"""
	# Get a unique name for the image	
	self.new_image_name = self.get_unique_image_name()
	
	# Create a new image to be removed
	(output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
	self.assertEqual(returncode, 0)

	# Run the 'remove-image' or 'ri' command. The 'yes yes' is used to pass 'yes' to the confirmation prompt
	# Here the function run_repoman_command is not used since 'yes yes |' has to precede repoman.
	p = Popen('yes yes | repoman %s %s' % (command, self.new_image_name), shell=True, stdout=PIPE, stderr=STDOUT)
        output = p.communicate()[0]
	m = re.search(r'OK.*Removed image', output)
	self.assertTrue( m != None)
	self.assertEqual(p.returncode, 0)
	
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

    # Test the optional parameter '--force'
    def test_remove_image_force(self):
	# Get unique image name and create image	
	self.new_image_name = self.get_unique_image_name()
	(output, returncode) = self.run_repoman_command('create-image %s' % (self.new_image_name))
        self.assertEqual(returncode, 0)
	
	# Run 'repoman remove-image --force' 
	(output, returncode) = self.run_repoman_command('remove-image --force %s' % (self.new_image_name))
	m = re.search(r'OK.*Removed image', output)
        self.assertTrue( m != None)
        self.assertEqual(returncode, 0)
	
	# Check if the image is removed and can't be seen in list-images
        (output, returncode) = self.run_repoman_command('list-images')
        m = re.search(self.new_image_name, output)
        self.assertTrue( m == None)




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






#####################################################################
#               COMMAND - 'repoman unshare-image-with-groups'
#####################################################################


class UnshareImageWithGroupsTest(RepomanCLITest):

    def UnshareImageWithGroups(self, command, arg):
	"""
	This method is called whenever the 'unshare-image-with-groups' or 'uig' command is used. The arguments are command and arg. 
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









#####################################################################
#####################################################################
#####################################################################




#
# The entrypoint into the script.
# No need to modify this at this point.
#

if __name__ == '__main__':
    unittest.main()
